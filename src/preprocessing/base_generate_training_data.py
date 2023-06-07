"""
generates training data for huggingface upload
"""

import os
import uuid
from typing import Dict, List, Tuple

import pandas as pd
from dotenv import load_dotenv
from huggingface_hub import DatasetCard, DatasetCardData, HfApi
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tomark import Tomark

from src.settings import Settings
from src.utils.data import get_size, load_json, save_parameters, transform_df_to_dict

dotenv_path = ".env"
load_dotenv(dotenv_path)

settings = Settings(_env_file="paths/.env.dev")


def replace_old_labels_in_annotated_data(
    doc: Dict, mdk_taxonomy_v2_to_mdk_taxonomy_v3_mapper: Dict
) -> None:
    """replaces the old labels of the taxonomy (v2) to new (v2)

    Parameters
    ----------
    doc : Dict
        document with annotation
    mdk_taxonomy_v2_to_mdk_taxonomy_v3_mapper : Dict
        mapper which contains two columns: v2 label name and v2 label name
    """
    for annotation in doc["annotations"]:
        if annotation["label"] in mdk_taxonomy_v2_to_mdk_taxonomy_v3_mapper:
            annotation["label"] = mdk_taxonomy_v2_to_mdk_taxonomy_v3_mapper[
                annotation["label"]
            ]


def transform_augmented_data(augmented_data: pd.DataFrame) -> pd.DataFrame:
    """transforms manually created augmented data

    Parameters
    ----------
    augmented_data : pd.DataFrame
        augmented data file

    Returns
    -------
    augmented_data; pd.DataFrame
        returns augmented data with doc id
    """
    # adding doc uuid to the manually created augmented data
    augmented_data["doc_id"] = [uuid.uuid4() for i in range(0, len(augmented_data))]

    return augmented_data


def transform_new_elinor_export(new_export: Dict) -> List[Dict]:
    """transforms data with the new elinor export

    Parameters
    ----------
    new_export : List[Dict[Any, Any]]
        elinor export data

    Returns
    -------
    annotations: List[Dict]
       returns data in format same as other data to concatenate with
    """
    annotations = []
    for doc in new_export["documents"]:
        if doc["annotations"]:
            current_document = {}
            current_document["title"] = doc["attributes_flat"]["dct:title"]
            current_document["description"] = doc["attributes_flat"]["dct:description"]
            current_document["doc_id"] = doc["attributes_flat"]["id"]
            current_document["labels_name"] = (
                doc["annotations"][0]["concept"]["broader_concept"]["preferred_label"][
                    "name"
                ]
                + " - "
                + doc["annotations"][0]["concept"]["preferred_label"]["name"]
            )
            annotations.append(current_document)
    return annotations


def transform_annotations(annotated_docs: List) -> List[Dict]:
    """transform the annotation into a list of dictionary with each dictionary
    representing one example.

    Parameters
    ----------
    annotated_docs : List
        documentations with annotations

    Returns
    -------
    List[Dict]
        Each dictionary represents one example. Variables: title, description, labels_name
    """
    # getting all the annotations first
    annotations = []
    for doc in annotated_docs:  # todo: default for text if None -> "None"
        current_document = {}
        # text
        full_text = (
            doc["text"].split("STOP DESCRIPTION START MUSTERDATENSATZ")[0].strip()
        )  # delete musterdatensatz from text
        current_document["title"] = full_text.split("STOP TITLE START DESCRIPTION")[
            0
        ].strip()  # only title
        current_document["description"] = full_text.split(
            "STOP TITLE START DESCRIPTION"
        )[
            1
        ].strip()  # only description

        # doc id
        current_document["doc_id"] = doc["id"]
        current_document["labels_name"] = doc["annotations"][0]["label"]
        annotations.append(current_document)
    return annotations


def add_index_label(df: pd.DataFrame):
    """generates an integer for each unique label and adds it to the training data as a separate column

    Parameters
    ----------
    df : pd.DataFrame
        training data with title, description and labels_name

    Returns
    -------
    _type_
        _description_
    """
    label_encoder = LabelEncoder()
    df["labels"] = label_encoder.fit_transform(df["labels_name"])
    return df


def train_test_split_stratified(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """splits the data into test and training data ensuring that at least each label occurs
    one time in the training data

    Parameters
    ----------
    df : pd.DataFrame
        training data with title, description, labels_name, and labels

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        splittet data into train and test
    """
    frequencies_labels = df.groupby("labels_name").size().reset_index(name="absolute")
    labels_with_one_example = list(
        frequencies_labels[frequencies_labels["absolute"] == 1]["labels_name"].unique()
    )
    without_one_example_labels = df[~df["labels_name"].isin(labels_with_one_example)]
    df_with_one_example_labels = df[df["labels_name"].isin(labels_with_one_example)]
    train, test = train_test_split(
        without_one_example_labels,
        test_size=0.2,
        stratify=without_one_example_labels["labels_name"],
    )
    train = pd.concat([train, df_with_one_example_labels])
    return (train, test)


def manual_label_fix(training_data, doc_id: str, new_label: str):
    """changes labels manually in the training data

    Parameters
    ----------
    training_data : _type_
        training data
    doc_id : str
        doc_id
    new_label : str
        new name, which should be assigned
    """
    if len(training_data[training_data["doc_id"] == doc_id]) == 1:
        index = training_data[training_data["doc_id"] == doc_id].index[0]

        current_label = training_data.loc[index, "labels_name"]
        training_data.at[index, "labels_name"] = new_label
        if training_data.loc[index, "labels_name"] == new_label:
            print(f"Label of doc: {doc_id} changed from {current_label} to {new_label}")
    else:
        print(f"doc id {doc_id} not found. No changes!")


def save_dataset(
    train: pd.DataFrame,
    train_path: str,
    is_test: bool,
    test: pd.DataFrame = pd.DataFrame(),
    test_path: str = "",
) -> None:
    """saves the training data to a provided path

    Parameters
    ----------
    train : pd.DataFrame
        training data
    train_path : str
        path for training data
    is_test : bool
        indicates whether a test dataset exists. If True and no test dataset and path are provided
        and empty dataframe will be saved in the root directory!
    test : pd.DataFrame, optional
        test data, by default pd.DataFrame()
    test_path : str, optional
        path for test data, by default ""
    """
    train.to_csv(
        path_or_buf=train_path,
        index=False,
    )

    if is_test:
        test.to_csv(
            path_or_buf=test_path,
            index=False,
        )


def upload_to_hub(
    dir: str,
    commit_message="upload",
) -> None:
    """uploads the provided path to the hub

    Parameters
    ----------
    dir : str
        file which contains all files, which should be uploaded
    commit_message : str, optional
        Commit message., by default "upload"
    """

    hf_api = HfApi()

    hf_api.upload_folder(
        folder_path=dir,
        path_in_repo=".",
        repo_type="dataset",
        repo_id="and-effect/mdk_gov_data_titles_clf",
        token=os.environ.get("HF_TOKEN"),
        commit_message=commit_message,
    )


if __name__ == "__main__":
    parameters: Dict = {"card_data": {}, "content": {}}
    annotated_docs: List = load_json(path=str(settings.ANNOTATED_DOCS))

    mdk_taxonomy_v2_to_mdk_taxonomy_v3 = pd.read_csv(
        filepath_or_buffer=f"{settings.BASE_PATH_ANNOTATIONS}/mapper/v2_v3_mapper.csv",
        sep=";",
    )

    mdk_taxonomy_v2_to_mdk_taxonomy_v3_mapper = transform_df_to_dict(
        df=mdk_taxonomy_v2_to_mdk_taxonomy_v3,
        key_column="v2_labels",
        value_column="v3_labels",
    )

    for doc in annotated_docs:
        replace_old_labels_in_annotated_data(
            doc=doc,
            mdk_taxonomy_v2_to_mdk_taxonomy_v3_mapper=mdk_taxonomy_v2_to_mdk_taxonomy_v3_mapper,
        )

    annotated_docs_processed = transform_annotations(annotated_docs=annotated_docs)

    # adding in augmented data
    augmented_data_raw = pd.read_csv(
        f"{settings.BASE_PATH_ANNOTATIONS}/augmentation_round/data_augmentation.csv",
        delimiter=";",
    )
    augmented_data_processed = transform_augmented_data(augmented_data_raw)

    training_data = pd.DataFrame(annotated_docs_processed)

    # adding in re-labeling with new elinor export style with same encoding
    relabeling_raw = load_json(
        f"{settings.BASE_PATH_ANNOTATIONS}/validation_round/2023-01-16T13-28-14_annotations.json"
    )
    relabeling_processed = transform_new_elinor_export(relabeling_raw)
    relabeling_processed = pd.DataFrame(relabeling_processed)

    # concat augmented with training
    training_data = pd.concat(
        [training_data, augmented_data_processed, relabeling_processed],
        ignore_index=True,
    )

    # fix parent only labels
    training_data = training_data[training_data["labels_name"].str.contains("-")]

    # fix description None
    training_data.loc[training_data["description"] == "None", "description"] == "NONE"

    # fix same title but different labels
    manual_label_fix(
        training_data=training_data,
        doc_id="b86eb9c7-b529-4a11-90d8-0dd920804288",
        new_label="Politische Partizipation - Wahl - Straßenverzeichnis",
    )

    manual_label_fix(
        training_data=training_data,
        doc_id="07334820-02af-481e-80e2-4277114e1173",
        new_label="Politische Partizipation - Wahl - Wahllokal",
    )

    manual_label_fix(
        training_data=training_data,
        doc_id="0db45bf9-5d7e-4346-ae0a-001074713031",
        new_label="Bevölkerungsstruktur - Staatsangehörigkeit",
    )

    manual_label_fix(
        training_data=training_data,
        doc_id="f145bace-4836-46d5-a013-dd6611a9f451",
        new_label="Abfallentsorgung - Abfallkalender",
    )

    manual_label_fix(
        training_data=training_data,
        doc_id="38ba61ae-f684-4bae-9a02-5cfa1eeb1a98",
        new_label="Raumordnung, Raumplanung und Raumentwicklung - Stadtplan",
    )

    manual_label_fix(
        training_data=training_data,
        doc_id="3ed230d4-8bc7-432a-a43a-b29117dd5b0d",
        new_label="Raumordnung, Raumplanung und Raumentwicklung - Stadtplan",
    )

    manual_label_fix(
        training_data=training_data,
        doc_id="1faedb9a-7913-4380-b4ee-3fe6699105b8",
        new_label="Sonstiges - Sonstiges",
    )

    manual_label_fix(
        training_data=training_data,
        doc_id="15ccd198-5a7c-4292-8a17-c14c38cd33d7",
        new_label="Sonstiges - Sonstiges",
    )

    manual_label_fix(
        training_data=training_data,
        doc_id="1629e052-0386-4934-b561-e782e8815e9f",
        new_label="Sonstiges - Sonstiges",
    )

    manual_label_fix(
        training_data=training_data,
        doc_id="cc6b2780-7d98-446e-970c-0e7088c7fbf0",
        new_label="Sonstiges - Sonstiges",
    )
    manual_label_fix(
        training_data=training_data,
        doc_id="d49a2ca5-c4ee-499b-a83e-c48f1f1f25f9",
        new_label="Verkehr - KFZ - Elektrotankstelle",
    )
    manual_label_fix(
        training_data=training_data,
        doc_id="acba0d45-8c30-45ee-bea0-4faabcbb304b",
        new_label="Bildung - Volkshochschule - Veranstaltung",
    )

    # adding index
    training_data = add_index_label(training_data)

    training_data = training_data[
        ["doc_id", "title", "description", "labels_name", "labels"]
    ]

    # splitting in training and validation
    validation_data = training_data.iloc[
        len(training_data) - len(relabeling_processed) :, :  # noqa: E203
    ]

    validation_data.to_csv(
        f"{settings.BASE_PATH_HUGGINGFACE}/small/validation.csv", index=False
    )
    validation_data.to_csv(
        f"{settings.BASE_PATH_HUGGINGFACE}/large/validation.csv", index=False
    )

    training_data = training_data.iloc[
        : len(training_data) - len(relabeling_processed), :
    ]

    # create small dataset
    training_data_small = training_data.sample(n=50)
    train_small, test_small = train_test_split(training_data_small)

    save_dataset(
        train=train_small,
        train_path=f"{settings.BASE_PATH_HUGGINGFACE}/small/train.csv",
        is_test=True,
        test=test_small,
        test_path=f"{settings.BASE_PATH_HUGGINGFACE}/small/test.csv",
    )

    train_large, test_large = train_test_split_stratified(training_data)

    # exclude "sonstige" class and fix with manually annotated data
    # wrong "sonstig" class training dataset

    save_dataset(
        train=train_large,
        train_path=f"{settings.BASE_PATH_HUGGINGFACE}/large/train.csv",
        is_test=True,
        test=test_large,
        test_path=f"{settings.BASE_PATH_HUGGINGFACE}/large/test.csv",
    )

    # without neutral class

    # Data Set Card
    parameters["content"][
        "dataset_summary"
    ] = f"The dataset is an annotated corpus of {len(training_data)} records from 'gov data'. The annotation maps the record titles to a taxonomy containing categories such as 'Verkehr - KFZ - Messung' or 'Abfallwirtschaft - Abfallkalender'.  Through the assignment the names of the data sets can be normalized and grouped. In total, the taxonomy consists 250 categories. /n The repository contains a small and a large version of the data. The small version is for testing purposes only. The large data set contains all 1009 entries. The large and small datasets are split into a training and a testing dataset. In addition, each folder contains a validation dataset that has been annotated separately."  # noqa: E501

    parameters["content"]["data_size"] = Tomark.table(
        [
            {
                "dataset": "small/train",
                "size": get_size(f"{settings.BASE_PATH_HUGGINGFACE}/small/train.csv"),
            },
            {
                "dataset": "small/test",
                "size": get_size(f"{settings.BASE_PATH_HUGGINGFACE}/small/test.csv"),
            },
            {
                "dataset": "large/train",
                "size": get_size(f"{settings.BASE_PATH_HUGGINGFACE}/large/train.csv"),
            },
            {
                "dataset": "large/test",
                "size": get_size(f"{settings.BASE_PATH_HUGGINGFACE}/large/test.csv"),
            },
        ]
    )

    parameters["content"]["dataset_split"] = Tomark.table(
        [
            {
                "dataset_name": "dataset_large",
                "dataset_splits": "train, test",
                "train_size": len(train_large),
                "test_size:": len(test_large),
            },
            {
                "dataset_name": "dataset_small",
                "dataset_splits": "train, test",
                "train_size": len(train_small),
                "test_size:": len(test_small),
            },
        ]
    )

    parameters["card_data"] = {
        "language": "de",
        "annotations_creators": "crowdsourced",
        "language_creators": "other",
        "task_categories": ["text-classification"],
        "multilinguality": "monolingual",
        "size_categories": "n>1K",
        "source_datasets": "extended",
        "pretty_name": "GOVDATA dataset titles labelled",
    }

    save_parameters(
        path="card_templates/dataset_parameters.json", parameters=parameters
    )

    dataset_card_parameters = load_json(path="card_templates/dataset_parameters.json")

    card_data = DatasetCardData(**dataset_card_parameters["card_data"])

    card = DatasetCard.from_template(
        template_path="card_templates/dataset_card_base.md",
        card_data=card_data,
        **dataset_card_parameters["content"],
    )

    card.save("data/hg_datasets/README.md")

    upload_to_hub(
        dir=str(settings.BASE_PATH_HUGGINGFACE),
        commit_message="upload small and large training data with same validation set",
    )

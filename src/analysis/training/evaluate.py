"""This file evaluates the performance of the current ML Model on the first and second level.
The test data is preprocessed because some labels are not assigned correctly"""


from typing import Dict, List

import pandas as pd
from datasets import load_dataset
from dotenv import load_dotenv
from huggingface_hub import EvalResult, ModelCard, ModelCardData
from tomark import Tomark

from src.components.bert_sim import BertSim
from src.settings import Settings
from src.utils.data import load_json
import os

settings = Settings(_env_file="paths/.env.dev")

MODEL_PATH = "and-effect/musterdatenkatalog_clf"
CORPUS_PATH = settings.TAXONOMY_PROCESSED_V3

EXCLUDE_LABELS = 2

dotenv_path = ".env"
load_dotenv(dotenv_path)


def correct_data(data: pd.DataFrame, mapper: Dict) -> pd.DataFrame:
    """function used to correct data with mapper

    Parameters
    ----------
    data : pd.DataFrame
        data to be corrected
    mapper : Dict
       mapper containing the old and new values

    Returns
    -------
    pd.DataFrame
        returns the corrected data
    """
    for key, value in mapper.items():
        data.loc[
            data["labels_name"] == key,
            "labels_name",
        ] = value
    return data


def correct_labels(current_data: pd.DataFrame, data_corrected: Dict) -> pd.DataFrame:
    """corrects with a manually labelled file all data labelled as
    "Sonstige" with the correct label if exists

    Parameters
    ----------
    current_data : DatasetDict
        dataset with incorrect labels
    data_corrected : pd.DataFrame
        dataset with corrected labels

    Returns
    -------
    pd.DataFrame
        current data set replaced with all correct labels if category is
        "Sonstige"
    """
    data_processed = []
    for el in data_corrected["documents"]:
        title = el["text"]
        doc_id = el["attributes_flat"]["doc_id"]
        description = el["attributes_flat"]["description"]
        bezeichnung = el["annotations"][0]["concept"]["preferred_label"]["name"]
        if el["annotations"][0]["concept"]["broader_concept"]:
            thema = el["annotations"][0]["concept"]["broader_concept"][
                "preferred_label"
            ]["name"]
        else:
            thema = "Sonstige"
            print(bezeichnung)

        data_processed.append(
            {
                "doc_id": doc_id,
                "title": title,
                "description": description,
                "labels_name": thema + " - " + bezeichnung,
                "label": -1,
            }
        )

    data_processed_df = pd.DataFrame(data_processed)
    data_processed_ids = list(data_processed_df["doc_id"])
    current_data_correct = current_data[
        ~current_data["doc_id"].isin(data_processed_ids)
    ]
    current_data_incorrect_ids = list(
        current_data[current_data["doc_id"].isin(data_processed_ids)]["doc_id"]
    )

    data_processed_corrections = data_processed_df[
        data_processed_df["doc_id"].isin(current_data_incorrect_ids)
    ]

    current_data_processed = pd.concat(
        [current_data_correct, data_processed_corrections]
    )
    current_data_processed = current_data_processed[
        current_data_processed["labels_name"] != "Sonstiges - Sonstiges"
    ]
    current_data_processed = current_data_processed[
        current_data_processed["labels_name"] != "Sonstige - Sonstige"
    ]

    return current_data_processed


def create_corpus(taxonomy: pd.DataFrame) -> List:
    """creates from the current taxonomy a list with all categories

    Parameters
    ----------
    taxonomy : pd.DataFrame
        columns THEMA und BEZEICHNUNG

    Returns
    -------
    List
        List of categories
    """
    corpus = list(set([f"{el['group']} - {el['label']}" for el in taxonomy]))
    corpus.remove("Sonstiges - Sonstiges")
    return corpus


def report_eval_result(result: float, metric_type: str, metric_name: str) -> EvalResult:
    """creates evaluation result object for model card

    Parameters
    ----------
    result : float
        model performance
    metric_type : str
        metric like recall, accuracy
    metric_name : str
        description name

    Returns
    -------
    EvalResult
        _description_
    """
    eval_result = EvalResult(
        task_type="text-classification",
        dataset_type="and-effect/mdk_gov_data_titles_clf",
        dataset_name="and-effect/mdk_gov_data_titles_clf",
        metric_type=metric_type,
        metric_value=result,
        metric_name=metric_name,
        dataset_split="test",
        dataset_revision="172e61bb1dd20e43903f4c51e5cbec61ec9ae6e6",  # pragma: allowlist secret
    )

    return eval_result


if __name__ == "__main__":
    # Load Corpus and Data
    eval_results_args = []
    results_args = []

    current_data = load_dataset(
        "and-effect/mdk_gov_data_titles_clf",
        data_dir="large",
        use_auth_token=True,
        revision="172e61bb1dd20e43903f4c51e5cbec61ec9ae6e6",  # pragma: allowlist secret
    )

    validation_data = load_dataset(
        "and-effect/mdk_gov_data_titles_clf", data_dir="large", use_auth_token=True
    )

    current_data = current_data["test"].to_pandas()

    data_corrected = load_json(
        path="data/annotations/augmentation_round/2023-01-17T09-50-23_annotations.json"
    )

    corpus_raw = load_json(path=str(settings.TAXONOMY_PROCESSED_V3))

    corpus = create_corpus(taxonomy=corpus_raw)

    current_data_corrected = correct_labels(
        current_data=current_data, data_corrected=data_corrected
    )
    # implement mapper changes
    mapper_v3_v4_data = pd.read_excel(
        f"{settings.BASE_PATH_ANNOTATIONS}/mapper/2023_02_21_v3_v4_mapper.xlsx"
    )
    mapper_v3_v4 = dict(zip(mapper_v3_v4_data.old, mapper_v3_v4_data.new))

    current_data_corrected = correct_data(current_data_corrected, mapper_v3_v4)

    texts = list(current_data_corrected["title"])
    labels = list(current_data_corrected["labels_name"])

    # Load Model
    bert_sim = BertSim(model=MODEL_PATH, corpus=corpus)

    # Evaluation Bezeichnung Level
    print("***Evaluation of test data***")
    print("Result on Level 'Bezeichnung'")
    predicted_docs = bert_sim.predict(queries=texts)
    predictions = [doc["prediction"] for doc in predicted_docs]
    report = bert_sim.classification_report_macro(predictions, labels)

    eval_results_args.append(
        report_eval_result(
            result=float(report["accuracy"]),
            metric_type="accuracy",
            metric_name="Accuracy 'Bezeichnung'",
        )
    )
    eval_results_args.append(
        report_eval_result(
            result=float(report["precision_macro"]),
            metric_type="precision",
            metric_name="Precision 'Bezeichnung' (macro)",
        )
    )
    eval_results_args.append(
        report_eval_result(
            result=float(report["recall_macro"]),
            metric_type="recall",
            metric_name="Recall 'Bezeichnung' (macro)",
        )
    )
    eval_results_args.append(
        report_eval_result(
            result=float(report["f1_macro"]),
            metric_type="f1",
            metric_name="Recall 'Bezeichnung' (macro)",
        )
    )

    report["task"] = "Test dataset 'Bezeichnung' I"
    results_args.append(report)

    # Evaluation Thema Level
    print("Result on Level 'Thema'")
    predictions_thema = [
        prediction.split("-")[0].rstrip() for prediction in predictions
    ]
    y_true_thema = [el.split("-")[0].rstrip() for el in labels]
    report = bert_sim.classification_report_macro(predictions_thema, y_true_thema)

    eval_results_args.append(
        report_eval_result(
            result=float(report["accuracy"]),
            metric_type="accuracy",
            metric_name="Accuracy 'Thema'",
        )
    )
    eval_results_args.append(
        report_eval_result(
            result=float(report["precision_macro"]),
            metric_type="precision",
            metric_name="Precision 'Thema' (macro)",
        )
    )
    eval_results_args.append(
        report_eval_result(
            result=float(report["recall_macro"]),
            metric_type="recall",
            metric_name="Recall 'Thema' (macro)",
        )
    )
    eval_results_args.append(
        report_eval_result(
            result=float(report["f1_macro"]),
            metric_type="f1",
            metric_name="Recall 'Thema' (macro)",
        )
    )

    report["task"] = "Test dataset 'Thema' I"
    results_args.append(report)

    # Exclude ill-defined
    print(
        f"Result on Level 'Bezeichnung' excluding labels with less than {EXCLUDE_LABELS}"
    )
    predicted_docs = bert_sim.predict(queries=texts)
    predictions = [doc["prediction"] for doc in predicted_docs]
    report = bert_sim.classification_report_macro(
        predictions, labels, exclude_not_predicted=EXCLUDE_LABELS, corpus=corpus
    )

    report["task"] = "Test dataset 'Bezeichnung' II"
    results_args.append(report)

    # updating validation data
    validation_data = validation_data["validation"].to_pandas()
    validation_data = correct_data(validation_data, mapper_v3_v4)

    texts = validation_data["title"]
    labels = validation_data["labels_name"]

    # Evaluation Bezeichnung Level validation
    print("***Evaluation of validation data***")
    print("Result on Level 'Bezeichnung'")
    predicted_docs = bert_sim.predict(queries=texts)
    predictions = [doc["prediction"] for doc in predicted_docs]
    report = bert_sim.classification_report_macro(predictions, labels)

    report["task"] = "Validation dataset 'Bezeichnung' I"
    results_args.append(report)

    print(report)

    # Evaluation Thema Level validation
    print("Result on Level 'Thema'")
    predictions_thema = [
        prediction.split("-")[0].rstrip() for prediction in predictions
    ]
    y_true_thema = [el.split("-")[0].rstrip() for el in labels]
    report = bert_sim.classification_report_macro(predictions_thema, y_true_thema)
    print(report)

    report["task"] = "Validation dataset 'Thema' I"
    results_args.append(report)

    # Exclude ill-defined
    print(
        f"Result on Level 'Bezeichnung' excluding labels with less than {EXCLUDE_LABELS}"
    )
    predicted_docs = bert_sim.predict(queries=texts)
    predictions = [doc["prediction"] for doc in predicted_docs]
    report = bert_sim.classification_report_macro(
        predictions, labels, exclude_not_predicted=EXCLUDE_LABELS, corpus=corpus
    )
    report["task"] = "Validation dataset 'Bezeichnung' II"
    results_args.append(report)

    # Create Model Card
    model_card_parameters: Dict = load_json(
        path="card_templates/model_card_parameters.json"
    )

    model_card_parameters["card_data"]["metrics"] = [
        "accuracy",
        "precision",
        "recall",
        "f1",
    ]

    result_args_formatted = Tomark.table(
        [
            {
                "***task***": report["task"],
                "***acccuracy***": report["accuracy"],
                "***precision (macro)***": report["precision_macro"],
                "***recall (macro)***": report["recall_macro"],
                "***f1 (macro)***": report["f1_macro"],
            }
            for report in results_args
        ]
    )

    model_card_parameters["content"]["results"] = result_args_formatted

    model_card_parameters["card_data"]["eval_results"] = eval_results_args

    card_data = ModelCardData(**model_card_parameters["card_data"])

    card = ModelCard.from_template(
        template_path="card_templates/model_card_base.md",
        card_data=card_data,
        **model_card_parameters["content"],
    )

    card.save("test_if_correct_model.md")

    card.push_to_hub(
        repo_id="and-effect/musterdatenkatalog_clf",
        token=os.environ.get("HF_TOKEN"),
        repo_type="model",
        commit_message="upload model performance",
    )

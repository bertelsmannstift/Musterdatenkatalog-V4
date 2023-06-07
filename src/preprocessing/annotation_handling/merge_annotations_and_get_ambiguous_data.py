"""create training data"""
import glob
from typing import Dict, List

import pandas as pd

from src.settings import Settings
from src.utils.data import load_json, save_json, transform_df_to_dict


def transform_annotations_to_wide_format(
    annotated_docs: List[Dict], document_id_uuid_mapper: Dict
) -> List[Dict]:
    """tranforms the annotation into wide format

    Parameters
    ----------
    annotated_docs : List[Dict]
        documents with annotations
    document_id_uuid_mapper : Dict
        mapper with two columns: document_id, uuid_id

    Returns
    -------
    List[Dict]
        each dictionary represents one document, with uuid id, text and annotation
    """
    annotated_docs_wide: List[Dict] = []
    same_documents = 0
    for doc in annotated_docs:
        uuid = document_id_uuid_mapper[doc["id"]]
        if len(doc["annotations"]) != 0:  # handle documents with no annotations
            is_not_in_annotation = True
            for el in annotated_docs_wide:
                if el["id"] == uuid:
                    same_documents += 1
                    el["annotations"].append(
                        {"concept": {"id": doc["annotations"][0]["concept"]["id"]}}
                    )
                    is_not_in_annotation = False

            if is_not_in_annotation:
                current_document: Dict = {}
                current_document["id"] = uuid
                current_document["text"] = doc["text"]
                current_document["annotations"] = [
                    {"concept": {"id": doc["annotations"][0]["concept"]["id"]}}
                ]
                annotated_docs_wide.append(current_document)
    return annotated_docs_wide


def add_concept_label(annotated_doc: Dict, concept_id_label_mapper: Dict) -> Dict:
    """adds the concept label to id

    Parameters
    ----------
    annotated_doc : Dict
        document with annotation
    concept_id_label_mapper : Dict
        mapper with two columns: concept_id, concept_label

    Returns
    -------
    Dict
        annotated doc with added concept label
    """
    for annotation in annotated_doc["annotations"]:
        annotation["concept"]["label"] = concept_id_label_mapper[
            annotation["concept"]["id"]
        ]
    return annotated_doc


def check_no_overlap_ids(docs_a: List[Dict], docs_b: List[Dict]) -> None:
    """check if uuids are unique for each document

    Parameters
    ----------
    docs_a : List[Dict]
        document collection
    docs_b : List[Dict]
        document collection for comparison

    Raises
    ------
    ValueError
       if there is an intersection between both collections Value Error is raised
    """
    docs_a_uuids = set([el["id"] for el in docs_a])
    docs_b_uuids = set([el["id"] for el in docs_b])

    if len(docs_a_uuids.intersection(docs_b_uuids)) > 0:
        raise ValueError("UUIDS are not distinctive")


def get_ambiguous_data(annotated_docs) -> pd.DataFrame:
    """collect all ambiguious documents

    Parameters
    ----------
    annotated_docs : _type_
        documents with annotation

    Returns
    -------
    pd.DataFrame
        table with all ambigious data
    """
    ambiguous_data = []
    for doc in annotated_docs:
        annotations = doc["annotations"]
        if len(annotations) > 1:
            if is_different_annotations(annotations=annotations):
                for annotation in annotations:
                    ambiguous_data.append(
                        {
                            "id": doc["id"],
                            "concept": annotation["concept"]["label"],
                            "text": doc["text"],
                        }
                    )
    return pd.DataFrame(ambiguous_data)


def concat_parent(
    annotated_data: List[Dict], child_id_parent_label_mapper: Dict
) -> None:
    """concats the labels to one string (Musterdatensatz)

    Parameters
    ----------
    annotated_data : List[Dict]
        documents with annotations
    child_id_parent_label_mapper : Dict
        mapper with two columns: child_id and parent label
    """

    for doc in annotated_data:
        for annotation in doc["annotations"]:
            if annotation["concept"]["id"] in child_id_parent_label_mapper:
                annotation["concept"][
                    "label"
                ] = f'{child_id_parent_label_mapper[annotation["concept"]["id"]]} - {annotation["concept"]["label"]}'  # noqa: E501


def is_different_annotations(annotations: List[Dict]) -> bool:
    """checks if a document has different label annotations

    Parameters
    ----------
    annotations : List[Dict]
        documents with annotations

    Returns
    -------
    bool
        if more than one label returns False
    """
    if len(set([el["concept"]["label"] for el in annotations])) > 1:
        return True
    else:
        return False


if __name__ == "__main__":
    settings = Settings(_env_file="paths/.env.dev")
    MAPPER_BASE_PATH = f"{settings.BASE_PATH_ANNOTATIONS}/mapper"
    ANNOTATION_BASE_PATH = settings.BASE_PATH_ANNOTATIONS
    TEST_ROUND_ANNOTATION_PATH = (
        f"{settings.ANNOTATIONS_DATA}testrunde/2022-12-20T09-47-39_annotations.json"
    )
    ROUNDS = 4

    # Load data
    annotated_docs_test_round = load_json(path=TEST_ROUND_ANNOTATION_PATH)

    annotated_docs_per_round = [
        load_json(
            path=glob.glob(
                f"{ANNOTATION_BASE_PATH}/ROUND_0{annotation_round}/annotations/*.json"
            )[0]
        )
        for annotation_round in range(1, ROUNDS + 1)
    ]

    # get mappers
    mdk_taxonomy_v1_concept_id_label_name = pd.read_csv(
        f"{MAPPER_BASE_PATH}/mdk_taxonomy_v1_concept_id_label_name_mapper.csv"
    )
    mdk_taxonomy_v2_concept_id_label_name = pd.read_csv(
        f"{MAPPER_BASE_PATH}/mdk_taxonomy_v2_concept_id_label_name_mapper.csv"
    )

    mdk_taxonomy_v1_parent_child = pd.read_csv(
        f"{MAPPER_BASE_PATH}/mdk_taxonomy_v1_parent_child_mapper.csv"
    )
    mdk_taxonomy_v2_parent_child = pd.read_csv(
        f"{MAPPER_BASE_PATH}/mdk_taxonomy_v2_parent_child_mapper.csv"
    )

    annotation_document_id_uuid = pd.read_csv(
        f"{MAPPER_BASE_PATH}/document_uuid_mapper.csv"
    )

    mdk_taxonomy_v1_concept_id_label_name_mapper = transform_df_to_dict(
        df=mdk_taxonomy_v1_concept_id_label_name,
        key_column="concept_id",
        value_column="name",
    )

    mdk_taxonomy_v2_concept_id_label_name_mapper = transform_df_to_dict(
        df=mdk_taxonomy_v2_concept_id_label_name,
        key_column="concept_id",
        value_column="name",
    )

    annotation_document_id_uuid_mapper = transform_df_to_dict(
        df=annotation_document_id_uuid, key_column="document_id", value_column="value"
    )

    mdk_taxonomy_v1_child_id_parent_label_mapper = transform_df_to_dict(
        df=mdk_taxonomy_v1_parent_child,
        key_column="child_id",
        value_column="parent_name",
    )

    mdk_taxonomy_v2_child_id_parent_label_mapper = transform_df_to_dict(
        df=mdk_taxonomy_v2_parent_child,
        key_column="child_id",
        value_column="parent_name",
    )

    # add Sonstiges as extra id since no child label
    mdk_taxonomy_v1_child_id_parent_label_mapper[
        "429fc156-01a8-44b5-bc1a-b23dfcbce443"
    ] = "Sonstiges"

    mdk_taxonomy_v2_child_id_parent_label_mapper[
        "a89b0ece-8afd-47ed-84e6-d0b33eb47cfc"
    ] = "Sonstiges"

    # transform annotation data per round to wide format and add concept label
    annotated_docs_wide_per_round = [
        transform_annotations_to_wide_format(
            annotated_docs=docs_per_round,
            document_id_uuid_mapper=annotation_document_id_uuid_mapper,
        )
        for docs_per_round in annotated_docs_per_round
    ]

    annotated_docs_wide_with_concept_label = [
        add_concept_label(
            annotated_doc=doc,
            concept_id_label_mapper=mdk_taxonomy_v2_concept_id_label_name_mapper,
        )
        for docs_per_round in annotated_docs_wide_per_round
        for doc in docs_per_round
    ]

    # add concept label to annotated_docs_test
    annotated_docs_test_round_with_concept_label = [
        add_concept_label(
            doc, concept_id_label_mapper=mdk_taxonomy_v1_concept_id_label_name_mapper
        )
        for doc in annotated_docs_test_round
    ]

    # add parent label to both annotated_datas
    concat_parent(
        annotated_data=annotated_docs_wide_with_concept_label,
        child_id_parent_label_mapper=mdk_taxonomy_v2_child_id_parent_label_mapper,
    )

    concat_parent(
        annotated_data=annotated_docs_test_round_with_concept_label,
        child_id_parent_label_mapper=mdk_taxonomy_v1_child_id_parent_label_mapper,
    )

    annotated_docs_with_ambiguous_data = (
        annotated_docs_wide_with_concept_label
        + annotated_docs_test_round_with_concept_label
    )

    ambiguous_data = get_ambiguous_data(
        annotated_docs=annotated_docs_with_ambiguous_data
    )

    ambiguous_data.to_excel(f"{ANNOTATION_BASE_PATH}/ambiguous_data.xlsx")

    save_json(
        obj=annotated_docs_with_ambiguous_data,
        path=f"{settings.BASE_PATH_ANNOTATIONS}/annotated_docs_with_ambiguous_data.json",
    )

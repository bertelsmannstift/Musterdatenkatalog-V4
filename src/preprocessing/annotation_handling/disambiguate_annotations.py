"""this file disambiguates documents with more than one annotations,
replace v1 labels with v2 labels and delete all duplicate annotations"""

from typing import Dict, List

import pandas as pd

from src.settings import Settings
from src.utils.data import load_json, save_json, transform_df_to_dict

settings = Settings(_env_file="paths/.env.dev")


def replace_old_labels_in_annotated_data(
    doc: Dict, mdk_taxonomy_v1_to_mdk_taxonomy_v2_mapper: Dict
) -> None:
    """transfer annotated data from v1 taxonomy to v2

    Parameters
    ----------
    doc : Dict
        document with annotations
    mdk_taxonomy_v1_to_mdk_taxonomy_v2_mapper : Dict
        mapper with columns: v1 label names, v2 label names
    """
    for annotation in doc["annotations"]:
        if annotation["concept"]["label"] in mdk_taxonomy_v1_to_mdk_taxonomy_v2_mapper:
            annotation["concept"]["label"] = mdk_taxonomy_v1_to_mdk_taxonomy_v2_mapper[
                annotation["concept"]["label"]
            ]


def disambiguate(
    doc: Dict,
    solved_doc_ids_and_concept_mapper: Dict,
    concept_name_concept_id_mapper: Dict,
) -> None:
    """loads manually disambiguated docs and replace them with one correct annotation

    Parameters
    ----------
    doc : Dict
        document with annotations
    solved_doc_ids_and_concept_mapper : Dict
        document with correct annotation
    concept_name_concept_id_mapper : Dict
        mapper with two columns: concept_id and concept_name
    """
    if doc["id"] in solved_doc_ids_and_concept_mapper:
        concept_name = solved_doc_ids_and_concept_mapper[doc["id"]]
        concept_id = concept_name_concept_id_mapper[concept_name]
        doc["annotations"] = [{"concept": {"id": concept_id, "label": concept_name}}]
    pass


def check_no_ambiguation(annotations: List) -> None:
    """checks if there are no ambiguations in the annotation data

    Parameters
    ----------
    annotations : List
        all annotations

    Raises
    ------
    ValueError
        if there are more than one label for a annotated document a value error will be raised,
    """
    if len(set([annotation["concept"]["label"] for annotation in annotations])) > 1:
        print(annotations)
        raise ValueError("ambiguous data found!")


def remove_duplicate_annotations(doc: Dict) -> None:
    """by taking the first annotation in the list all duplicate annotations are removed.
    Annotations have to be disambiguated before

    Parameters
    ----------
    doc : Dict
        doc with annotations
    """
    doc["annotations"] = [doc["annotations"][0]["concept"]]


def check_no_duplicate_annotations(doc: Dict) -> None:
    """checks the number of annotations per document and raises an Value Error if more than
    one annotation

    Parameters
    ----------
    doc : Dict
        document with annotations

    Raises
    ------
    ValueError
        if more than one annotation per document raises Value Error
    """
    if len(doc["annotations"]) > 1:
        raise ValueError("duplicate annotation found!")


if __name__ == "__main__":
    ANNOTATED_DATA_BASE_PATH = str(settings.BASE_PATH_ANNOTATIONS)

    MAPPER_BASE_PATH = f"{settings.BASE_PATH_ANNOTATIONS}/mapper"

    # load data
    ambiguous_data_solved = pd.read_excel(
        f"{ANNOTATED_DATA_BASE_PATH}/ambiguous_data_solved.xlsx"
    )

    annotated_docs_with_ambiguous_data = load_json(
        f"{ANNOTATED_DATA_BASE_PATH}/annotated_docs_with_ambiguous_data.json"
    )

    # load mapper
    mdk_taxonomy_v1_to_mdk_taxonomy_v2 = pd.read_csv(
        f"{MAPPER_BASE_PATH}/v1_v2_mapper.csv", sep=";"
    )

    mdk_taxonomy_v2_parent_child = pd.read_csv(
        f"{MAPPER_BASE_PATH}/mdk_taxonomy_v2_parent_child_mapper.csv"
    )

    mdk_taxonomy_v1_to_mdk_taxonomy_v2_mapper = transform_df_to_dict(
        df=mdk_taxonomy_v1_to_mdk_taxonomy_v2,
        key_column="v1_labels",
        value_column="v2_labels",
    )

    solved_doc_ids_and_concepts_mapper = transform_df_to_dict(
        df=ambiguous_data_solved, key_column="id", value_column="concept"
    )

    for key, value in solved_doc_ids_and_concepts_mapper.items():
        if value in mdk_taxonomy_v1_to_mdk_taxonomy_v2_mapper:
            solved_doc_ids_and_concepts_mapper[
                key
            ] = mdk_taxonomy_v1_to_mdk_taxonomy_v2_mapper[value]

    mdk_taxonomy_v2_parent_child["parent_child_label"] = (
        mdk_taxonomy_v2_parent_child["parent_name"]
        + " - "
        + mdk_taxonomy_v2_parent_child["child_name"]
    )

    concept_name_concept_id_mapper = transform_df_to_dict(
        df=mdk_taxonomy_v2_parent_child,
        key_column="parent_child_label",
        value_column="child_id",
    )

    concept_name_concept_id_mapper[
        "Sonstiges - Sonstiges"
    ] = "a89b0ece-8afd-47ed-84e6-d0b33eb47cfc"

    for doc in annotated_docs_with_ambiguous_data:
        replace_old_labels_in_annotated_data(
            doc, mdk_taxonomy_v1_to_mdk_taxonomy_v2_mapper
        )
        disambiguate(
            doc, solved_doc_ids_and_concepts_mapper, concept_name_concept_id_mapper
        )
        check_no_ambiguation(annotations=doc["annotations"])
        remove_duplicate_annotations(doc=doc)
        check_no_duplicate_annotations(doc=doc)

    save_json(
        obj=annotated_docs_with_ambiguous_data,
        path=str(settings.ANNOTATED_DOCS),
    )

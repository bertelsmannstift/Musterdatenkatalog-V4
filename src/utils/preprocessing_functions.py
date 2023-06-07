"""
script including often used functions in the process taxonomy file. Used to do and track changes
"""

import os
from csv import DictWriter
from typing import List, Literal, Union

import numpy as np
import pandas as pd

from src.settings import Settings

settings = Settings(_env_file="paths/.env.dev")


# configuratin for the tracking file
field_names = [
    "alter Thema Name",
    "neuer Thema Name",
    "alte Bezeichnung",
    "neue Bezeichnung",
    "Art der Änderung",
]

excel_log = pd.DataFrame(columns=field_names)
excel_log.to_csv(
    os.path.join(str(settings.LOGGER_PATH), "logger_migration.csv"), index=False
)


def track_taxonomy_change(func):
    """decorator tracking the changes of either taxonomy or data"""

    def decorator(*args, **kwargs):

        df = {
            "alter Thema Name": kwargs.get("old_group_name", None),
            "neuer Thema Name": kwargs.get("new_group_name", None),
            "alte Bezeichnung": kwargs.get("old_label_name", None),
            "neue Bezeichnung": kwargs.get("new_label_name", None),
            "Art der Änderung": func.__name__,
        }

        with open(
            os.path.join(settings.LOGGER_PATH, "logger_migration.csv"), "a"
        ) as f_object:
            dictwriter_object = DictWriter(f_object, fieldnames=field_names)
            dictwriter_object.writerow(df)
            f_object.close()
        return func(*args, **kwargs)

    return decorator


@track_taxonomy_change
def taxonomy_delete_concept(
    taxonomy: List,
    old_group_name: Union[str, None],
    old_label_name: Union[str, None],
    node_type: Literal["group", "label", "all"],
) -> List:
    """deltes a given concept from the used taxonomy

    Parameters
    ----------
    taxonomy : List
        flat taxonomy
    old_group_name : Union[str, None]
        the old group name to be deleted
    old_label_name : Union[str, None]
        the old label name to be deleted
    node_type : Literal[&quot;group&quot;, &quot;label&quot;, &quot;all&quot;]
        the node type, either group meaning all with this group name delted,
        label meaning everything with this label deleted or
        all meaning only those with combination of given group and label name

    Returns
    -------
    List
        returns processed taxonomy as flat list

    Raises
    ------
    ValueError
        checks if group name given if node type group
    ValueError
        checks of label name given if node type label
    ValueError
        checks if both group name and label name given if node type all
    """

    if node_type == "group":
        if old_group_name is None:
            raise ValueError("group not given")
        else:
            taxonomy_processed = list(
                filter(lambda x: x["group"] != old_group_name, taxonomy)
            )

    if node_type == "label":
        if old_label_name is None:
            raise ValueError("label not given")
        else:
            taxonomy_processed = list(
                filter(lambda x: x["label"] != old_label_name, taxonomy)
            )

    if node_type == "all":
        if old_group_name is None or old_label_name is None:
            raise ValueError("group or label missing")
        taxonomy_processed = list(
            filter(
                lambda x: (x["label"], x["group"]) != (old_label_name, old_group_name),
                taxonomy,
            )
        )
    return taxonomy_processed


@track_taxonomy_change
def taxonomy_add_concept(
    taxonomy: List,
    new_group_name: str,
    new_label_name: str,
) -> List:
    """adds concept to taxonomy

    Parameters
    ----------
    taxonomy : List
        current taxonomy
    new_group_name : str
        group name of new entry
    new_label_name : str
        label name of new entry

    Returns
    -------
    List
        new taxonomy with new entry as flat list
    """
    taxonomy.append({"label": new_label_name, "group": new_group_name})
    return taxonomy


@track_taxonomy_change
# flake8: noqa: C901
def taxonomy_rename_concept(
    taxonomy: List,
    old_group_name: Union[str, None],
    new_group_name: Union[str, None],
    old_label_name: Union[str, None],
    new_label_name: Union[str, None],
    node_type: Literal["label", "group", "all"],
) -> List:
    """renames a concept in the taxonomy

    Parameters
    ----------
    taxonomy : List
        current taxonomy
    old_group_name : Union[str, None]
        the old group name
    new_group_name : Union[str, None]
       the new group name
    old_label_name : Union[str, None]
        the old label name
    new_label_name : Union[str, None]
       the new label name
    node_type : Literal[&quot;label&quot;, &quot;group&quot;, &quot;all&quot;]
        node type can either be label meaning concepts with this name rename,
        group meaning renaming all concepts with this group name
        or all meaning rename concepts with given group and label name

    Returns
    -------
    List
       returns new taxonomy

    Raises
    ------
    ValueError
        raises error if node type label but no old and new label given
    ValueError
       raises error if node type group but no old and new group name given
    ValueError
       raises error if node type all but no old and new group name and no old and new label name given
    """

    if node_type == "label":
        if old_label_name is None or new_label_name is None:
            raise ValueError("no old or new label given")
        for dic in taxonomy:
            if dic["label"] == old_label_name:
                dic["label"] = new_label_name

    if node_type == "group":
        if old_group_name is None or new_group_name is None:
            raise ValueError("no old or new group given")
        for dic in taxonomy:
            if dic["group"] == old_group_name:
                dic["group"] = new_group_name

    if node_type == "all":
        if (
            old_group_name is None
            or new_group_name is None
            or old_label_name is None
            or new_label_name is None
        ):
            raise ValueError("no old or new label/group given")
        for dic in taxonomy:
            if dic["group"] == old_group_name and dic["label"] == old_label_name:
                dic["group"] = new_group_name
                dic["label"] = new_label_name

    return taxonomy


@track_taxonomy_change
# flake8: noqa: C901
def taxonomy_rename_or_delete_concept(
    taxonomy: List,
    old_group_name: Union[str, None],
    new_group_name: Union[str, None],
    old_label_name: Union[str, None],
    new_label_name: Union[str, None],
) -> List:
    """renames or deletes a concept in the taxonomy

    Parameters
    ----------
    taxonomy : List
        current taxonomy
    old_group_name : Union[str, None]
        the old group name
    new_group_name : Union[str, None]
       the new group name
    old_label_name : Union[str, None]
        the old label name
    new_label_name : Union[str, None]
       the new label name

    Returns
    -------
    List
       returns new taxonomy

    Raises
    ------

    ValueError
       raises error if no old and new group name and no old and new label name given
    """
    if (
        old_group_name is None
        or new_group_name is None
        or old_label_name is None
        or new_label_name is None
    ):
        raise ValueError("no old or new label/group given")
    for dic in taxonomy:
        if dic["group"] == old_group_name and dic["label"] == old_label_name:
            dic["group"] = new_group_name
            dic["label"] = new_label_name

    return taxonomy


@track_taxonomy_change
def data_rename_concept(
    data: pd.DataFrame,
    old_group_name: Union[str, List[str], None],
    new_group_name: Union[str, List[str], None],
    old_label_name: Union[str, List[str], None],
    new_label_name: Union[str, List[str], None],
    node_type: Literal["group", "label"],
) -> pd.DataFrame:
    """renames all entries in the data with given group and label name

    Parameters
    ----------
    data : pd.DataFrame
        data with all entries
    old_group_name : Union[str, List[str], None]
       the old group name
    new_group_name : Union[str, List[str], None]
       the new group name
    old_label_name : Union[str, List[str], None]
        the old label name
    new_label_name : Union[str, List[str], None]
        the new label name
    node_type : Literal[&quot;group&quot;, &quot;label&quot;]
        node type, either group if all within group renamed or
        label only with specific label renamed

    Returns
    -------
    pd.DataFrame
        new data with renamed entries

    Raises
    ------
    ValueError
       raise error if no node type given
    ValueError
        raise error if node type group but no old and new group name given
    ValueError
        raise error if node type label but no old and new label name given
    """

    if node_type != "group" and node_type != "label":
        raise ValueError("wrong node type given")
    if node_type == "group":
        if old_group_name is None or new_group_name is None:
            raise ValueError("no old or new label given")
        data["THEMA"].replace({old_group_name: new_group_name}, inplace=True)

    if node_type == "label":
        if old_label_name is None or new_label_name is None:
            raise ValueError("no old or new label given")
        data["BEZEICHNUNG"].replace({old_label_name: new_label_name}, inplace=True)
    # iterating over to update andy changes in Bezeichnung or group

    data["MUSTERDATENSATZ"] = data["THEMA"] + " - " + data["BEZEICHNUNG"]

    return data


@track_taxonomy_change
def data_move_concept(
    data: pd.DataFrame,
    old_group_name: Union[str, List[str]],
    new_group_name: Union[str, List[str]],
    old_label_name: Union[str, List[str]],
    new_label_name: Union[str, List[str]],
) -> pd.DataFrame:
    """moves a concept in the data (renaming of both group and label in one step)

    Parameters
    ----------
    data : pd.DataFrame
        data with all entries
    old_group_name : Union[str, List[str]]
        the old group name
    new_group_name : Union[str, List[str]]
        the new group name
    old_label_name : Union[str, List[str]]
        the old label name
    new_label_name : Union[str, List[str]]
        the new label name

    Returns
    -------
    pd.DataFrame
        new modified data
    """

    for index, row in data.iterrows():
        if row["THEMA"] == old_group_name and row["BEZEICHNUNG"] == old_label_name:
            data.loc[index, ["THEMA"]] = new_group_name
            data.loc[index, ["BEZEICHNUNG"]] = new_label_name
    # iterating over to update andy changes in Bezeichnung or group
    data["MUSTERDATENSATZ"] = data["THEMA"] + " - " + data["BEZEICHNUNG"]
    return data


@track_taxonomy_change
def data_delete_concept(
    data: pd.DataFrame,
    old_group_name: Union[str, None],
    old_label_name: Union[str, None],
    node_type: Literal["group", "label", "all"],
) -> pd.DataFrame:
    """deletes a concept from the data

    Parameters
    ----------
    data : pd.DataFrame
       data with all entries
    old_group_name : Union[str, None]
       the old group name
    old_label_name : Union[str, None]
        the old label name
    node_type : Literal[&quot;group&quot;, &quot;label&quot;, &quot;all&quot;]
        node type either group meaning delete all with this group,
        label meaning delete all with this label name or
        all meaning delete all with this group and label name combination

    Returns
    -------
    pd.DataFrame
        changed data frame

    Raises
    ------
    ValueError
        raise error if node type group but no group name given
    ValueError
        raise error if node type label but no label name given
    ValueError
        raise error if node type all but either no group or label name given
    """

    if node_type == "group":
        if old_group_name is None:
            raise ValueError("no group given")
        data["THEMA"] = np.where((data.THEMA == old_group_name), None, data.THEMA)
    if node_type == "label":
        if old_label_name is None:
            raise ValueError("no label given")
        data["BEZEICHNUNG"] = np.where(
            (data.BEZEICHNUNG == old_label_name), None, data.BEZEICHNUNG
        )
    if node_type == "all":
        if old_group_name is None or old_label_name is None:
            raise ValueError("group or label not given")
        for index, row in data.iterrows():
            if row["THEMA"] == old_group_name and row["BEZEICHNUNG"] == old_label_name:
                data.loc[index, ["THEMA"]] = None
                data.loc[index, ["BEZEICHNUNG"]] = None

    data["MUSTERDATENSATZ"] = data["THEMA"] + " - " + data["BEZEICHNUNG"]

    return data


def generate_excel_log() -> None:
    """generates the excel log from the process file"""
    csv_log = pd.read_csv(
        os.path.join(str(settings.LOGGER_PATH), "logger_migration.csv")
    )
    csv_log.to_excel(
        os.path.join(str(settings.LOGGER_PATH), "logger_migration.xlsx"), index=False
    )

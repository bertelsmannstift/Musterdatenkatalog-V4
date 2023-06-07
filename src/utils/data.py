"""
script with functions for data import and saving and
data analysis used in the data exploration process
"""

import itertools
import json
import os
from typing import Any, Dict, List, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix


def load_json(path: str) -> Any:
    """loads a json file

    Parameters
    ----------
    path : str
       path to json file

    Returns
    -------
    List[Any]
        list of the json data
    """
    with open(file=path, mode="r") as fp:
        data = json.load(fp=fp)
    return data


def save_json(obj: Union[List, Dict], path: str) -> None:
    """saves a json file

    Parameters
    ----------
    obj : Union[List, Dict]
        the json data
    path : str
        path specifying where to store the json file
    """
    with open(file=path, mode="w") as fp:
        json.dump(obj=obj, fp=fp)


def count_categories(
    df: pd.DataFrame,
    column_name: str,
    top: Union[int, None] = None,
    limit: Union[int, None] = None,
) -> pd.DataFrame:
    """counts the entries of a specified column in a dataframe

    Parameters
    ----------
    df : pd.DataFrame
        input dataframe with column to be counted
    column_name : str
        column with values to count
    top : Union[int, None], optional
        upper limit of count, for later visualization usefull
    limit : Union[int, None], optional
        lower limit of count, for later visualization usefull

    Returns
    -------
    pd.DataFrame
       dataframe including the count for each category
    """
    df_count_ = (
        df.groupby(by=[column_name])
        .count()["uuid"]
        .reset_index()
        .sort_values(by=["uuid"], ascending=False)
    )
    if top:
        df_count = df_count_[:top]
    elif limit:
        df_count = df_count_[df_count_["uuid"] > limit]
        print(f"Excluded catgories: {len(df_count_) - len(df_count)}")
    else:
        df_count = df_count_
    return df_count


def make_distribution_fig(
    df_count: pd.DataFrame,
    df: pd.DataFrame,
    counter: str,
    variable: str,
    mode: str,
    xlabel: Union[str, None] = None,
    title: Union[str, None] = None,
) -> None:
    """produces distribution visualizations

    Parameters
    ----------
    df_count : pd.DataFrame
        data including the variable to count for plot
    df : pd.DataFrame
        general data
    counter : str
        which unique variable used as counter, f.e. uuid
    variable : str
        which variable frequency to plot
    mode : str
        either distribution or percentage, controls visualiuzation display
    xlabel : Union[str, None], optional
        name of x label
    title : Union[str, None], optional
        name of visusalization

    Returns
    -------
    None
        plots visualization
    """
    fig, ax = plt.subplots(figsize=(20, 5))
    if mode == "distribution":
        ax.bar(
            df_count[variable],
            edgecolor="white",
            linewidth=0.5,
            height=df_count[counter],
            color="#FE563E",
        )
    if mode == "percentage":
        ax.bar(
            edgecolor="white",
            linewidth=0.5,
            x=df_count[variable],
            height=df_count[counter] / len(df),
            color="#FE563E",
        )
    ax.tick_params(axis="x", rotation=90)
    plt.xticks(fontsize=5, rotation=90)
    ax.set(xlabel=xlabel)

    ax.set_title(title, fontsize=18)
    ax.grid(axis="x")
    plt.show()


def create_co_occurences_matrix(
    allowed_words: List[str], documents: List[str]
) -> Union[Dict, Any]:
    """creates the co-occurence matrix of two input lists

    Parameters
    ----------
    allowed_words : List[str]
        first flat list of unique words
    documents : List[Any]
        nested lists of words

    Returns
    -------
    Union[Dict, Any]
       returns the word coocurrence matrix and a dict with word to id mapping
    """
    word_to_id = dict(zip(allowed_words, range(len(allowed_words))))
    documents_as_ids = [
        np.sort([word_to_id[w] for w in doc if w in word_to_id]).astype("uint32")
        for doc in documents
    ]
    row_ind, col_ind = zip(
        *itertools.chain(
            *[[(i, w) for w in doc] for i, doc in enumerate(documents_as_ids)]
        )
    )
    data = np.ones(
        len(row_ind), dtype="uint32"
    )  # use unsigned int for better memory utilization
    max_word_id = max(itertools.chain(*documents_as_ids)) + 1
    docs_words_matrix = csr_matrix(
        (data, (row_ind, col_ind)), shape=(len(documents_as_ids), max_word_id)
    )  # efficient arithmetic operations with CSR * CSR
    words_cooc_matrix = (
        docs_words_matrix.T * docs_words_matrix
    )  # multipl. docs_words_matrix with its transpose matrix would gen. the co-occurences matrix
    words_cooc_matrix.setdiag(0)
    return words_cooc_matrix, word_to_id


def transform_df_to_dict(df: pd.DataFrame, key_column: str, value_column: str) -> Dict:
    """transform two pandas columns to dictionary where one column
    is the key and one column is the value

    Parameters
    ----------
    df : pd.DataFrame
        data
    key_column : str
        column which should be transformed as key
    value_column : str
        column which should be transformed as value

    Returns
    -------
    Dict
        transformed columns as dictionary
    """
    return dict(zip(df[key_column], df[value_column]))


def load_txt(path: str) -> List:
    """loads textfile and parse as list

    Parameters
    ----------
    path : str
        path to textfile

    Returns
    -------
    List
        each line as one element in List
    """
    with open(path, "r") as f:
        return [line.rstrip("\n") for line in f]


def save_parameters(path: str, parameters: Dict) -> None:
    """collects parameters for dataset card and writes to a json file.
    If a parameter already exists and is provided it will be replaced. If not
    the old parameter will be kept.

    Parameters
    ----------
    path : str
        path of json file to save all parameters, if file does not exists
        a new file will be generated. The json file has the following format
        {"card_data": {}, "content": {}}
    parameters : _type_
        _description_
    """
    if os.path.isfile(path):
        current_dataset_parameters: Dict = load_json(path=path)
        if "card_data" in parameters:
            if "card_data" in current_dataset_parameters:
                for key, value in parameters["card_data"].items():
                    if key in current_dataset_parameters["card_data"]:
                        print(f"Replace parameter {key} with value: {value}")
                        current_dataset_parameters["card_data"][key] = value
                    else:
                        print(f"Add parameter {key} with value: {value}")
                        current_dataset_parameters["card_data"][key] = value
            else:
                current_dataset_parameters["card_data"] = parameters["card_data"]
        if "content" in parameters:
            if "content" in current_dataset_parameters:
                for key, value in parameters["content"].items():
                    if key in current_dataset_parameters["content"]:
                        print(f"Replace parameter {key} with value: {value}")
                        current_dataset_parameters["content"][key] = value
                    else:
                        print(f"Add parameter {key} with value: {value}")
                        current_dataset_parameters["content"][key] = value
            else:
                current_dataset_parameters["content"] = parameters["content"]
        save_json(path=path, obj=current_dataset_parameters)
    else:
        save_json(path=path, obj=parameters)


def get_size(path: str) -> Union[str, None]:
    """analyzes the size of data from given path

    Parameters
    ----------
    path : str
        path to data

    Returns
    -------
    Union[str, None]
        size of data
    """
    size = os.path.getsize(path)
    if size < 1024:
        return f"{size} bytes"
    elif size < pow(1024, 2):
        return f"{round(size/1024, 2)} KB"
    elif size < pow(1024, 3):
        return f"{round(size/(pow(1024,2)), 2)} MB"
    elif size < pow(1024, 4):
        return f"{round(size/(pow(1024,3)), 2)} GB"
    return None


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]  # noqa: E203

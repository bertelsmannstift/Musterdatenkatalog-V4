"""
parsing gov data downloading response
"""
import datetime
import glob
import json
import logging
import os
from typing import Dict, List, Union

import pandas as pd
import requests
from tqdm import tqdm

from src.settings import Settings

parsing_functions = []

settings = Settings(_env_file="paths/.env.dev")
current_date = datetime.datetime.now().date()

logger = logging.getLogger(name=__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    os.path.join(str(settings.LOGGER_PATH), "logger_parser_gov_data.log"), "w", "utf-8"
)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)


def load_responses(path: str) -> List[Dict]:
    """load json responses

    Parameters
    ----------
    path : str
        dir with json responses

    Returns
    -------
    List[Dict]
        responses
    """
    with open(file=path, mode="r") as fp:
        responses = json.load(fp=fp)
    return responses


def process_func_name(function) -> str:
    """get name of function name

    Parameters
    ----------
    function : function
        parsing function

    Returns
    -------
    str
        name of parsing function
    """
    return function.__name__[4:].replace("_", ":")


def register(function):
    """wrapper to register of parsing functions

    Parameters
    ----------
    function : function
        parsing function

    Returns
    -------
    function
        returns function
    """
    parsing_functions.append(function)
    return function


def get_data(function_list: List, dataset: Dict) -> Dict:
    """get data with all parsing function

    Parameters
    ----------
    function_list : List[function]
        list of parsing functions
    dataset : Dict
        _description_

    Returns
    -------
    Dict
        all metadata in dictionary with function of metadata as key and extraction as value
    """
    result = {process_func_name(function=func): func(dataset) for func in function_list}
    return result


@register
def get_dct_description(dataset: Dict) -> str:
    """gets the description of the dataset

    Parameters
    ----------
    dataset : Dict
        response with metadata

    Returns
    -------
    str
        description of the dataset
    """
    if "dct:description" in dataset:
        return dataset["dct:description"]
    else:
        logger.info("key dct:description not found, return nan")
        return "NONE"


@register
def get_dct_title(dataset: Dict) -> Union[float, str]:
    """gets the title of the dataset

    Parameters
    ----------
    dataset : Dict
        response with metadata

    Returns
    -------
    Union[float, str]
        if title exists the title will be returned, otherwise NA
    """
    if "dct:title" in dataset:
        return dataset["dct:title"]
    else:
        logging.info("key dct:title not found, return nan")
        return float("nan")


def get_dataset_response(data_url: str, dataset_name: str) -> List:
    """get request to get the metadata and extract for each datasetname
    the metadata of the type dcat:Dataset

    Parameters
    ----------
    data_url : str
        url for get request
    dataset_name : str
        name of the dataset

    Returns
    -------
    List
        responses for datasetname, filtered for dcat:Dataset
    """
    resp = requests.get(url=f"{data_url}/{dataset_name}.jsonld")
    response_data = resp.json()
    datasets = list(
        filter(lambda x: x["@type"] == "dcat:Dataset", response_data["@graph"])
    )
    return datasets


if __name__ == "__main__":

    data = []

    response_paths = glob.glob(pathname=f"{settings.ANNOTATIONS_DATA}/*.json")

    for response_path in tqdm(response_paths):
        response = load_responses(path=response_path)
        for el in response:
            uuid = response_path.split("/")[-1].split(".")[0]
            dct_title = get_dct_title(dataset=el)

            dct_description = get_dct_description(dataset=el)

            data.append(
                {
                    "id": uuid,
                    "dct:title": dct_title,
                    "dct:description": dct_description,
                }
            )

    df = pd.DataFrame(data=data)
    df[df["dct:description"].isna()]

    df["text"] = df[["dct:title", "dct:description"]].agg(
        " STOP TITLE START DESCRIPTION ".join, axis=1
    )

    df.to_csv(
        path_or_buf=f"data/raw/{current_date}_gov_meta_data_sets_per_category.csv",
        index=False,
    )

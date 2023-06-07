"""
script downloads data from gov data in jsonld format
"""

import json
import logging
import os
import random
from glob import glob
from hashlib import sha256
from pathlib import Path
from typing import Any, List

import requests
from tqdm import tqdm

from src.settings import Settings

settings = Settings(_env_file="paths/.env.dev")

logging.basicConfig(
    filename=os.path.join(str(settings.LOGGER_PATH), "logger_gov_download.log"),
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(name=__name__)


def _request(url: str) -> Any:
    """get result of response

    Parameters
    ----------
    url : str
        url for request

    Returns
    -------
    List
        result part of response
    """

    resp = requests.get(url=url)
    try:
        resp.raise_for_status()
    except Exception as e:
        logger.error(e)
    response = resp.json()
    return response


def get_current_dataset_list(current_dataset_url: str, sample_size: int = 1) -> List:
    """get a sample list of current datasets by dcat groups

    Parameters
    ----------
    base_url : str
        base url
    sample_size : int, optional
        number of datasets for each group, by default 50

    Returns
    -------
    List
        dataset names
    """
    group_list = _request(url=f"{current_dataset_url}/group_list")["result"]
    dataset_names: List[str] = []
    for group in group_list:
        group_url_datasets = f"{current_dataset_url}/package_list?fq=group:{group}"
        dataset_response = _request(url=group_url_datasets)["result"]
        sample = random.sample(dataset_response, k=sample_size)
        for el in sample:
            dataset_names.append(el)
    return dataset_names


def dataset_not_exists(dataset_name: str) -> bool:
    """checks if dataset already exists in the folder

    Parameters
    ----------
    dataset_name : str
        name of the dataset

    Returns
    -------
    bool
        if the dataset does not exists in the folder then true
    """
    not_exists = True
    path = str(settings.ANNOTATIONS_DATA)
    url = f"{DATASET_URL}/{dataset_name}.jsonld"
    hash_code = sha256(url.encode()).hexdigest()[:13]
    if os.path.exists(path):
        filenames = glob(f"{settings.ANNOTATIONS_DATA}/*.json")
        if hash_code in filenames:
            not_exists = False
            logging.info(msg=f"Dataset {url} with filename {hash_code} already exists.")
    return not_exists


def get_dataset(dataset_url: str, dataset_name: str) -> List:
    """request to get dataset by name

    Parameters
    ----------
    data_url : str
        base gov data url
    dataset_name : str
        name of dataset

    Returns
    -------
    List
        returns dcat: Dataset
    """
    response_data = _request(url=f"{dataset_url}/{dataset_name}.jsonld")
    datasets = list(
        filter(lambda x: x["@type"] == "dcat:Dataset", response_data["@graph"])
    )
    return datasets


def save_response(url: str, dataset_response: List) -> None:
    """save responses as json in a new folder

    Parameters
    ----------
    path : str
        path to save response
    """
    path = str(settings.ANNOTATIONS_DATA)
    Path(path).mkdir(parents=True, exist_ok=True)

    hash = sha256(url.encode()).hexdigest()[:13]
    with open(file=f"{path}/{hash}.json", mode="w") as fp:
        json.dump(dataset_response, fp)

    logger.info(f"Dataset {url} with id {hash} is successfully downloaded")


if __name__ == "__main__":
    CURRENT_DATASET_URL = "https://ckan.govdata.de/api/3/action"
    DATASET_URL = "https://www.govdata.de/ckan/dataset"

    dataset_names = get_current_dataset_list(current_dataset_url=CURRENT_DATASET_URL)

    for dataset_name in tqdm(dataset_names):

        if dataset_not_exists(dataset_name=dataset_name):
            dataset_response = get_dataset(
                dataset_url=DATASET_URL, dataset_name=dataset_name
            )

            save_response(
                url=f"{DATASET_URL}/{dataset_name}.jsonld",
                dataset_response=dataset_response,
            )

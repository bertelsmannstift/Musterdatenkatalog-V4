"""Pipeline component: scrapes data from gov data"""

import datetime
import logging
import os
import random
from pathlib import Path
from typing import List

import httpx
from joblib import Parallel, delayed
from tqdm import tqdm

from src.settings import Settings
from src.utils.data import chunks

settings = Settings(_env_file="paths/.env.dev")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(str(settings.LOGGER_PATH), "logger_pipeline.log")
        ),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(name=__name__)


class Scraper:
    def __init__(self) -> None:
        self.current_dataset_list: List = []
        self.current_dataset_url = "https://ckan.govdata.de/api/3/action"
        self.dataset_url = "https://www.govdata.de/ckan/dataset"

    def _request(self, url: str) -> httpx.Response:
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

        resp = httpx.get(url=url)
        try:
            resp.raise_for_status()
        except Exception as e:
            logger.error(e)
        return resp

    def get_current_dataset_list(self, sample_size: int = -1) -> None:
        """get a sample list of current datasets, if sample size is not set or set to -1
        all data current datasets from Gov Data will be scraped

        Parameters
        ----------
        base_url : str
            base url
        sample_size : int, optional
            number of datasets to be sample, -1 as default indicates to use all available data and not to perform sampling

        Returns
        -------
        List
            dataset names
        """

        dataset_response = self._request(
            url=f"{self.current_dataset_url}/package_list"
        ).json()["result"]

        if sample_size != -1:
            dataset_response = random.sample(dataset_response, k=sample_size)

        for el in dataset_response:
            self.current_dataset_list.append(el)
        now = datetime.datetime.now()
        output_file_path = os.path.join(
            "extraction",
            "musterdatenkatalog",
            f"{now.year}-{now.month}-{now.day}-current_dataset_list.txt",
        )
        # Open the file in write mode and write each element on a new line
        with open(output_file_path, "w") as file:
            for item in self.current_dataset_list:
                file.write(f"{item}\n")

    def save_response(self, resp: httpx.Response, file_directory: str) -> None:
        """save responses as json in a new folder

        Parameters
        ----------
        path : str
            path to save response
        """
        file_name = resp.url.path.split("/")[-1].split(".")[0] + ".xml"
        Path(file_directory).mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(file_directory, file_name)

        if not os.path.isfile(file_path):
            with open(file=file_path, mode="w") as fp:
                fp.write(resp.text)
            logger.info(f"Dataset {file_name} is successfully downloaded")
        else:
            logger.info(msg=f"Dataset {file_name} already exists.")

    def scrape(
        self,
        file_directory: str,
        sample_size: int = -1,
    ) -> None:
        """scrapes the data if sample size is not set or set to -1
        all data current datasets from Gov Data will be scraped


        Parameters
        ----------
        file_directory : str
            directory for saving files
        sample_size : int, optional
            sample size of current dataset, by default -1
        """
        self.get_current_dataset_list(sample_size=sample_size)
        for dataset_name in self.current_dataset_list:
            self.save_response(
                resp=self._request(url=f"{self.dataset_url}/{dataset_name}.rdf"),
                file_directory=file_directory,
            )

    def _batch_process(
        self,
        batch: List,
        file_directory: str,
    ) -> None:
        for dataset_name in batch:
            self.save_response(
                resp=self._request(url=f"{self.dataset_url}/{dataset_name}.rdf"),
                file_directory=file_directory,
            )

    def scrape_parallel(
        self,
        file_directory: str,
        sample_size: int = -1,
        batch_size=1000,
        current_dataset_list: List = None,
    ) -> None:
        if current_dataset_list:
            self.current_dataset_list = current_dataset_list
        else:
            self.get_current_dataset_list(sample_size=sample_size)
        self.current_dataset_list = [
            el
            for el in self.current_dataset_list
            if not os.path.isfile(os.path.join(file_directory, f"{el}.xml"))
        ]
        batches = [chunk for chunk in chunks(self.current_dataset_list, batch_size)]

        Parallel(n_jobs=-1)(
            delayed(self._batch_process)(batch, file_directory)
            for batch in tqdm(batches)
        )

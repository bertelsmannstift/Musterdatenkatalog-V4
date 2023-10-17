"""Pipeline component: parse data scraped from scraper.py.
Source: https://github.com/bertelsmannstift/Musterdatenkatalog (edited)"""

import logging
import os
from datetime import datetime
from pathlib import Path

import httpx
import pandas as pd
from bs4 import BeautifulSoup, Tag
from dateutil.parser import parse
from joblib import Parallel, delayed

from src.settings import Settings
from src.utils.data import chunks

settings = Settings(_env_file="paths/.env.dev")


if not os.path.exists("docs"):
    Path("docs").mkdir(parents=True, exist_ok=True)

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


class CustomisedTag(Tag):
    def find_tree(self, element_tree, *kwargs):
        result = self.find(element_tree.pop(0))
        if len(element_tree) > 0:
            for el in element_tree:
                result = result.find(el)
        return result

    def find_all_with_parent(self, element, parent, *kwargs):
        results = self.find_all(element, kwargs)
        return [result for result in results if result.parent.name == parent]

    def find_with_parent(self, element, parent, *kwargs):
        results = self.find_all(element, kwargs)
        for result in results:
            if result.parent.name == parent:
                return result
        return None


class Parser:
    def __init__(self, current_cities):
        self.categories = {}
        self.df = pd.read_csv(current_cities)

    def _read_file(self, file_path):
        with open(file_path) as f:
            content = f.read()
        return content

    def get_themes(self):
        url = "https://publications.europa.eu/resource/authority/data-theme"
        response = httpx.get(url)
        try:
            response.raise_for_status()
        except Exception as e:
            logger.error(e)
        response_soup = BeautifulSoup(response.text, "xml")
        categories_ = response_soup.find_all("rdf:Description")
        for c in categories_:
            try:
                url = c.get("rdf:about")
                if url not in self.categories:
                    category = BeautifulSoup(httpx.get(url).text, "xml").find(
                        "skos:prefLabel", {"xml:lang": "de"}
                    )
                    self.categories[url] = category
            except Exception as e:
                logger.info(
                    f"The theme could not be extracted. The following error occurred {e}"
                )

    def get_title(self):
        try:
            return (
                self.soup.find("dcat:dataset")
                .find_with_parent("dct:title", "dcat:dataset")
                .text
            )
        except Exception as e:
            logger.info(
                f"The title could not be extracted. The following error occurred {e}"
            )
            return float("nan")

    def get_license(self):
        try:
            return self.soup.find("dct:license").get("rdf:resource")
        except Exception as e:
            logger.info(
                f"The License could not be extracted. The following error occurred {e}"
            )
            return float("nan")

    def get_category(self, url):
        return self.categories.get(url, "")

    def get_categories(self):
        try:
            categories = self.soup.find_all("dcat:theme")
            return ", ".join(
                [self.get_category(c.get("rdf:resource")) for c in categories]
            )
        except Exception as e:
            logger.info(
                f"The category could not be extracted. The following error occurred: {e}"
            )
            return float("nan")

    def get_tags(self):
        try:
            tags = self.soup.find_all("dcat:keyword")
            return ", ".join([t.text for t in tags])
        except Exception as e:
            logger.info(
                f"The tag could not be extracted. The following error occurred: {e}"
            )
            return float("nan")

    def get_url(self):
        try:
            return self.soup.find("dcat:dataset").get("rdf:about")
        except Exception as e:
            logger.info(
                f"The url could not be extracted. The following error occurred: {e}"
            )
            return float("nan")

    def get_id(self):
        try:
            return self.soup.find("dct:identifier").text
        except Exception as e:
            logger.info(
                f"The id could not be extracted. The following error occurred: {e}"
            )
            return float("nan")

    def get_description(self):
        try:
            return (
                self.soup.find("dcat:dataset")
                .find_with_parent("dct:description", "dcat:dataset")
                .text
            )
        except Exception as e:
            logger.info(
                f"The description could not be extracted. The following error occurred: {e}"
            )
            return float("nan")

    def get_distribution_description(self):
        try:
            return ", ".join(
                [
                    t.text
                    for t in self.soup.find("dcat:dataset").find_all_with_parent(
                        "dct:description", "dcat:distribution"
                    )
                ]
            )
        except Exception as e:
            logger.info(
                f"The url could not be extracted. The following error occurred: {e}"
            )

            return float("nan")

    def get_updated_at(self):
        try:
            text = self.soup.find("dct:modified").text
            return datetime.strftime(parse(text), "%Y-%m-%d")
        except Exception as e:
            logger.info(
                f"The url could not be extracted. The following error occurred: {e}"
            )
            return float("nan")

    def get_city(self):
        cities_csv_logger = []
        col_tree_logger = []
        col_tree_logger_error = []
        columns = [
            ["vcard:fn"],
            ["dct:publisher", "foaf:name"],
            ["dcatde:maintainer", "foaf:name"],
            ["dct:maintainer", "foaf:name"],
            ["dct:creator", "foaf:name"],
        ]
        for col_tree in columns:
            try:
                tag = self.soup.find("dcat:dataset").find_tree(col_tree)
                stelle = tag.text
                if (
                    self.df["name"].str.contains(stelle).any()
                    or self.df["name"].eq(stelle).any()
                ):
                    row = self.df.loc[self.df["name"] == stelle, "Kommune"]
                    return row.array[0]
                else:
                    cities_csv_logger.append(stelle)
            except Exception as e:
                col_tree_logger.append(col_tree)
                col_tree_logger_error.append(e)
                continue
        if len(cities_csv_logger) > 0:
            logger.info(f"No name in cities.csv matches the tags {cities_csv_logger}")
        if len(col_tree_logger) > 0:
            logger.info(
                f"The {col_tree_logger} could not be extracted. The following error messages occurred {set(col_tree_logger_error)}"  # noqa: E501
            )
        logger.info(msg="The city could not be extracted")
        return float("nan")

    def get_data(self, file_path):
        return {
            "dct:title": self.get_title(),
            "dct:identifier": self.get_id(),
            "url": self.get_url(),
            "dct:description": self.get_description(),
            "distribution_description": self.get_distribution_description(),
            "city": self.get_city(),
            "license": self.get_license(),
            "categories": self.get_categories(),
            "tags": self.get_tags(),
            "updated_at": self.get_updated_at(),
            "added": datetime.strftime(datetime.now(), "%Y-%m-%d"),
            "file_path": file_path,
        }

    def parse_data(self, file_path):
        logger.info(msg=f"Parse {file_path}")
        self.content = self._read_file(file_path)
        self.soup = BeautifulSoup(
            self.content, "lxml", element_classes={Tag: CustomisedTag}
        )
        self.get_themes()
        data = self.get_data()
        for key, value in data.items():
            if value == "":
                data[key] = float("nan")
        return data

    def _batch_process(self, batch):
        result = []
        for file_path in batch:
            self.content = self._read_file(file_path)
            self.soup = BeautifulSoup(
                self.content, "lxml", element_classes={Tag: CustomisedTag}
            )
            data = self.get_data(file_path)
            for key, value in data.items():
                if value == "":
                    data[key] = float("nan")
            result.append(data)
        return result

    def parse_data_parallel(self, file_paths, batch_size=1000):
        self.get_themes()
        results = []
        batches = [chunk for chunk in chunks(file_paths, batch_size)]

        data_per_batch = Parallel(n_jobs=-1)(
            delayed(self._batch_process)(batch) for batch in batches
        )

        for batch in data_per_batch:
            for data in batch:
                results.append(data)
        return results

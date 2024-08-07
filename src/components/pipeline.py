"""This file extracts the "Musterdatenkatalog"
with the current data from GovData"""

import glob
import logging
import os
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from src.components.bert_sim import BertSim
from src.components.parser import Parser
from src.components.scraper import Scraper
from src.settings import Settings
from src.utils.data import load_json

settings = Settings(_env_file="paths/.env.dev")


GOV_DATA_RESPONSES = "extraction/gov_data_responses"
CURRENT_CITIES_PATH = settings.CITIES_V5
MODEL_PATH = "and-effect/musterdatenkatalog_clf"
CORPUS_PATH = settings.TAXONOMY_PROCESSED_V3
OUTPUT_PATH = "extraction/musterdatenkatalog"

SAMPLE_SIZE = -1

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


def _download_current_gov_data(sample_size):
    scraper = Scraper()
    if not os.path.exists(GOV_DATA_RESPONSES):
        logger.info("The GovData responses folder does not exist. Downloading...")
        Path("extraction/gov_data_responses").mkdir(parents=True, exist_ok=True)
        scraper.scrape_parallel(
            file_directory=GOV_DATA_RESPONSES, sample_size=sample_size, batch_size=1000
        )
        file_paths = glob.glob(pathname=os.path.join(GOV_DATA_RESPONSES, "*.xml"))
        return file_paths
    else:
        logger.info("The GovData responses folder already exists.")
        scraper.get_current_dataset_list()
        file_paths = glob.glob(pathname=os.path.join(GOV_DATA_RESPONSES, "*.xml"))
        file_paths_updated = check_if_all_files_are_downloaded(
            file_paths=file_paths, current_dataset_list=scraper.current_dataset_list
        )
        return file_paths_updated


def _create_corpus():
    if os.path.exists(settings.TAXONOMY_PROCESSED_V3):
        logger.info(msg="The corpus already exists.")
    else:
        from src.preprocessing.migration_taxonomy import generate_taxonomy  # noqa: F401
        from src.preprocessing.migration_taxonomy import process_taxonomy  # noqa: F401


def _load_corpus():
    corpus_raw = load_json(path="data/processed/taxonomy_processed_v3.json")
    corpus = list(set([f"{el['group']} - {el['label']}" for el in corpus_raw]))
    corpus.remove("Sonstiges - Sonstiges")
    return corpus


def check_if_all_files_are_downloaded(current_dataset_list, file_paths):
    file_paths_datasets = [el.split("/")[-1].split(".")[0] for el in file_paths]
    if set(current_dataset_list) == set(file_paths_datasets):
        return file_paths
    if len(set(current_dataset_list).difference(set(file_paths_datasets))) > 0:
        logger.info(
            "Some files are missing in the GovData responses folder. Downloading..."
        )
        scraper = Scraper()
        missing_datasets = list(
            set(current_dataset_list).difference(set(file_paths_datasets))
        )
        scraper.scrape_parallel(
            file_directory=GOV_DATA_RESPONSES, current_dataset_list=missing_datasets
        )
    if len(set(file_paths_datasets).difference(set(current_dataset_list))) > 0:
        logger.info(
            "In the GovData responses folder are files that are not in the current dataset list. Files will not be parsed, but will not be deleted."  # noqa: E501
        )
        logger.info(
            f"{len(set(file_paths_datasets).difference(set(current_dataset_list)))} files are not in the current dataset list."  # noqa: E501
        )
        file_paths_updated = [
            file_paths[idx]
            for idx, el in enumerate(file_paths_datasets)
            if el in current_dataset_list
        ]
        print(len(file_paths_updated))
        print(len(current_dataset_list))
        return file_paths_updated
    else:
        return glob.glob(pathname=os.path.join(GOV_DATA_RESPONSES, "*.xml"))


def main():
    logger.info(msg="***START PIPELINE***")
    logger.info(msg="CREATE CORPUS")
    _create_corpus()
    corpus = _load_corpus()

    file_paths = _download_current_gov_data(sample_size=SAMPLE_SIZE)

    parser = Parser(current_cities=CURRENT_CITIES_PATH)

    logger.info(msg=f"PARSING {len(file_paths)} FILES")

    all_data = parser.parse_data_parallel(file_paths=file_paths, batch_size=5)

    logger.info(msg=f"PARSED {len(all_data)} files.")
    data = [x for x in all_data if str(x["city"]) != "nan"]
    logger.info(
        msg=f"FILTERED OUT {len(all_data) - len(data)} ENTRIES DUE TO MISSING CITIES"
    )

    logger.info(msg="ENRICH DATA")
    bert_sim = BertSim(model=MODEL_PATH, corpus=corpus)
    for el in tqdm(data):
        prediction = bert_sim.predict([el["dct:title"]])
        el["thema"] = prediction[0]["prediction"].split("-")[0].rstrip()
        el["bezeichnung"] = prediction[0]["prediction"].split("-", 1)[1].lstrip()

    logger.info(msg=f"SAVE DATA IN {OUTPUT_PATH}")
    if not os.path.exists(OUTPUT_PATH):
        Path("extraction/musterdatenkatalog").mkdir(parents=True, exist_ok=True)

    pd.DataFrame(data).to_excel(
        os.path.join(OUTPUT_PATH, "musterdatenkatalog.xlsx"), index=False
    )
    pd.DataFrame(data).to_csv(
        os.path.join(OUTPUT_PATH, "musterdatenkatalog.csv"), index=False
    )
    return data


if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()

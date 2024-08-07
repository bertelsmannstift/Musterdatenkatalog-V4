from typing import Union

from pydantic import BaseSettings


class Settings(BaseSettings):
    # raw
    BASELINE_MDK_TRAINING_DATA: Union[str, None] = None
    BASELINE_MDK_ENRICHED_DATA: Union[str, None] = None
    PLURAL_NAMES: Union[str, None] = None
    SINGULAR_NAMES: Union[str, None] = None
    CITIES: Union[str, None] = None
    CITIES_V2: Union[str, None] = None
    CITIES_V3: Union[str, None] = None
    CITIES_V4: Union[str, None] = None
    CITIES_V5: Union[str, None] = None
    TAXONOMY_INFO_V1: Union[str, None] = None
    TAXONOMY_INFO_V2: Union[str, None] = None

    # processed
    TAXONOMY_PROCESSED_V1: Union[str, None] = None
    TAXONOMY_PROCESSED_V2: Union[str, None] = None
    TAXONOMY_PROCESSED_V3: Union[str, None] = None
    BASELINE_MDK_TRAINING_DATA_PROCESSED_V1: Union[str, None] = None
    BASELINE_MDK_TRAINING_DATA_PROCESSED_V2: Union[str, None] = None

    # Logger
    LOGGER_PATH: Union[str, None] = None

    # Annotations data
    ANNOTATIONS_DATA: Union[str, None] = None
    BASE_PATH_ANNOTATIONS_ROUNDS: Union[str, None] = None
    BASE_PATH_ANNOTATIONS: Union[str, None] = None
    ANNOTATED_DOCS: Union[str, None] = None

    BASE_PATH_HUGGINGFACE: Union[str, None] = None

    # Extraction Data
    EXTRACTION_DATA: Union[str, None] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

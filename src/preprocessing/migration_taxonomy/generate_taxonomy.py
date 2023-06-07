"""
script generates the old taxonomy by using the old data
It also does some first cleaning of the data (removing '-')
"""

import os
from pathlib import Path
from typing import Dict

import pandas as pd

from src.settings import Settings
from src.utils.data import save_json
from src.utils.preprocessing_functions import (  # noqa: E501
    data_move_concept,
    data_rename_concept,
)

settings = Settings(_env_file="paths/.env.dev")
df = pd.read_csv(settings.BASELINE_MDK_TRAINING_DATA)
df = df.dropna(subset=["MUSTERDATENSATZ"])

# cleaning data first of "-" words
df = data_rename_concept(
    data=df,
    old_group_name="Zivil- und Katastrophenschutz",
    new_group_name="Zivil und Katastrophenschutz",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)

df = data_move_concept(
    data=df,
    old_group_name="Fuhrpark",
    new_group_name="Fuhrpark",
    old_label_name="KFZ-Bestand",
    new_label_name="KFZ Bestand",
)
df = data_move_concept(
    data=df,
    old_group_name="Individualverkehr",
    new_group_name="Individualverkehr",
    old_label_name="KFZ-Bestand",
    new_label_name="KFZ Bestand",
)
df = data_rename_concept(
    data=df,
    old_group_name="Sport- und Spielstätten",
    new_group_name="Sport und Spielstätten",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)

df = data_rename_concept(
    data=df,
    old_group_name="Sport- und Spielplätze",
    new_group_name="Sport und Spielplätze",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)

df = data_move_concept(
    data=df,
    old_group_name="Kultur",
    new_group_name="Kultur",
    old_label_name="Lehr- und Wanderpfade",
    new_label_name="Lehr und Wanderpfade",
)
df = data_move_concept(
    data=df,
    old_group_name="Wirtschaft",
    new_group_name="Wirtschaft",
    old_label_name="Industrie- und Gewerbeflächen",
    new_label_name="Industrie und Gewerbeflächen",
)


themes_unique = list(df["THEMA"].unique())


mapper: Dict = {theme: [] for theme in themes_unique}

themes = df["THEMA"].to_list()
musterdatensaetze = df["MUSTERDATENSATZ"].to_list()

bezeichnungen = [el.split("-", 1)[1].lstrip() for el in musterdatensaetze]

for idx in range(0, len(themes)):
    mapper[themes[idx]].append(bezeichnungen[idx])

for theme, bezeichnungen in mapper.items():
    mapper[theme] = list(set(bezeichnungen))

taxonomy = [
    {"label": val, "group": key} for key, value in mapper.items() for val in value
]

if not os.path.exists("data/processed"):
    Path("data/processed").mkdir(parents=True, exist_ok=True)

save_json(obj=taxonomy, path=str(settings.TAXONOMY_PROCESSED_V1))

df.to_csv(path_or_buf=settings.BASELINE_MDK_TRAINING_DATA_PROCESSED_V1)

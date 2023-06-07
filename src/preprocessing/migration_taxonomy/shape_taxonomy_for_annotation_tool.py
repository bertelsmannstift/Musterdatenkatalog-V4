"""
Script for producing a taxonomy format that fits with Elinor
"""
import uuid

from src.settings import Settings
from src.utils.data import load_json, save_json

"""
desired format:
list of dict, Geisteswissenschften with child Soziologie
[
    {
        "description": "F01",
        "label_title": "Geisteswissenschaften",
        "label_uuid": "4ef32f04-79cd-4cbe-a704-95fb75662051",
        "parent_label_uuid": null,
        "color": "#2aa198",
        "alt_labels": []
    },
    {
        "description": "F02",
        "label_title": "Soziologie",
        "label_uuid": "d501ee02-93dd-4011-a832-61591ac2f139",
        "parent_label_uuid": "4ef32f04-79cd-4cbe-a704-95fb75662051",
        "color": "#268bd2",
        "alt_labels": []
    }]
"""

# Import of taxonomy
settings = Settings(_env_file="paths/.env.dev")
taxonomy = load_json(path=str(settings.TAXONOMY_PROCESSED_V2))

# newly shaped taxonomy
shaped_taxonomy = []

# generating first level
themes = set(concept["group"] for concept in taxonomy)

for group in themes:
    shaped_taxonomy.append(
        {
            "description": "",
            "label_title": group,
            "label_uuid": str(uuid.uuid4()),
            "parent_label_uuid": None,
            "color": None,
            "alt_labels": [],
        }
    )

# generating second level
for concept in taxonomy:
    parent = concept["group"]
    parent_uuid = next(
        item for item in shaped_taxonomy if item["label_title"] == parent
    )["label_uuid"]
    shaped_taxonomy.append(
        {
            "description": "",
            "label_title": concept["label"],
            "label_uuid": str(uuid.uuid4()),
            "parent_label_uuid": parent_uuid,
            "color": None,
            "alt_labels": [],
        }
    )

# sanity check -> no nested dictionaries
for concept in shaped_taxonomy:
    if isinstance(concept["label_title"], dict):
        raise ValueError(("dictionary detected"))

# save newly shaped taxonomy
save_json(obj=shaped_taxonomy, path="data/processed/taxonomy_elinor_format.json")

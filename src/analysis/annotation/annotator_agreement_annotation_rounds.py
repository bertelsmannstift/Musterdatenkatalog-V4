"""
analysis of the annotation rounds with old export format from elinor
"""

import glob
import itertools
import os
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import cohen_kappa_score

from src.settings import Settings
from src.utils.data import load_json

ROUND = "04"

settings = Settings(_env_file="paths/.env.dev")

documents = load_json(
    path=glob.glob(
        os.path.join(
            str(settings.BASE_PATH_ANNOTATIONS),
            f"Round_{ROUND}",
            "Annotations",
            "*.json",
        )
    )[0]
)


document_uuid_data = pd.read_csv(
    str(
        os.path.join(
            settings.BASE_PATH_ANNOTATIONS, "mapper", "document_uuid_mapper.csv"
        )
    )
)

document_uuid_mapper = dict(
    zip(document_uuid_data["document_id"], document_uuid_data["value"])
)

annotations: List = []
raters = []
counter = 0
for doc in documents:
    if len(doc["annotations"]) != 0:
        is_not_in_annotations = True
        uuid = document_uuid_mapper[doc["id"]]
        for el in annotations:
            if el["uuid"] == uuid:
                name = doc["annotations"][0]["annotator"]["name"]
                annotation_label = doc["annotations"][0]["concept"]["id"]
                el[name] = annotation_label
                is_not_in_annotations = False
                raters.append(name)
        if is_not_in_annotations:
            current_document = {}
            current_document["uuid"] = uuid
            name = doc["annotations"][0]["annotator"]["name"]
            annotation_label = doc["annotations"][0]["concept"]["id"]
            current_document[name] = annotation_label
            annotations.append(current_document)
            raters.append(name)
    else:
        counter += 1

print(counter)
raters = list(set(raters))

annotations_intersection = [el for el in annotations if len(el) > 2]

annotations_df = pd.DataFrame(annotations_intersection)

# # get the data for each rater
labelling = [annotations_df[rater].to_list() for rater in raters]

# # define an empty matrix
cohens_matrix = np.zeros((len(labelling), len(labelling)))

# # calculate between each rater the
for j, k in list(itertools.combinations(range(len(labelling)), r=2)):
    cohens_matrix[j, k] = cohen_kappa_score(labelling[j], labelling[k])

cohens_matrix[cohens_matrix == 0] = np.nan
cohens_kappa_avg = np.nanmean(a=cohens_matrix)
print(cohens_kappa_avg)

fig, ax = plt.subplots()
ax = sns.heatmap(
    cohens_matrix,
    mask=np.tri(len(labelling)),
    annot=True,
    linewidths=5,
    vmin=0,
    vmax=1,
    xticklabels=[f"Rater {k + 1}" for k in range(len(labelling))],
    yticklabels=[f"Rater {k + 1}" for k in range(len(labelling))],
)
ax.set_title("Cohens Kappa", fontsize=15)

ax.text(
    x=0.5,
    y=1.05,
    s=f"Cohens Kappa average value: {round(cohens_kappa_avg, ndigits=2)}",
    fontsize=8,
    alpha=0.75,
    ha="center",
    va="bottom",
    transform=ax.transAxes,
)

plt.show()

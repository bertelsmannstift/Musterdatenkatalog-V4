import itertools
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import cohen_kappa_score

from src.settings import Settings
from src.utils.data import load_json

settings = Settings(_env_file="paths/.env.dev")

documents = load_json(
    path=str(
        os.path.join(
            str(settings.BASE_PATH_ANNOTATIONS),
            "testrunde",
            "2022-12-20T09-47-39_annotations.json",
        )
    )
)

annotations = []
raters = []

for doc in documents:
    current_document = {}
    current_document["doc_id"] = doc["id"]
    for annotation in doc["annotations"]:
        name = annotation["annotator"]["name"]
        annotation_label = annotation["concept"]["id"]
        current_document[name] = annotation_label
        raters.append(name)
    annotations.append(current_document)

raters = list(set(raters))
annotations_df = pd.DataFrame(annotations)

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

"""
    script for exploration of the labelled data
    requirements:
    -label coverage
    -label distribution
    -inconsistency checks
    -check searchwords
    -identify new categories with "Sonstiges"
    -examples for category Auto und Schwerlastenverkehr
"""
import pandas as pd
from datasets import load_dataset

from src.settings import Settings
from src.utils.data import load_json, make_distribution_fig

settings = Settings(_env_file="paths/.env.dev")

# loading and combining train and test
train_test = load_dataset(
    "and-effect/mdk_gov_data_titles_clf",
    "large",
    revision="172e61bb1dd20e43903f4c51e5cbec61ec9ae6e6",  # pragma: allowlist secret
)
train = pd.DataFrame(train_test["train"])
test = pd.DataFrame(train_test["test"])
data = pd.concat([train, test])

# taxonomny
taxonomy = load_json(settings.TAXONOMY_PROCESSED_V2)
taxonomy_entries = [concept["group"] + " - " + concept["label"] for concept in taxonomy]

# labels annotated
annotated_labels = []
for index, entry in data.iterrows():
    annotated_labels.append(entry["labels_name"])


########
# Label distribution
########
count_labels = (
    data.groupby(by=["labels_name"])
    .count()["doc_id"]
    .reset_index()
    .sort_values(by=["doc_id"], ascending=False)
)
condensed_count_labels = count_labels[count_labels["doc_id"] > 6]
make_distribution_fig(
    df_count=condensed_count_labels,
    df=data,
    counter="doc_id",
    variable="labels_name",
    mode="percentage",
    title="Number of Datasets per label",
)

########
# Label coverage
#######

# intersection taxonomy labels and actually labelled
coverage_percent = len(
    list(set(annotated_labels).intersection(taxonomy_entries))
) / len(taxonomy_entries)
print("current coverage in percent", coverage_percent)

missing_labels = list(set(annotated_labels) ^ set(taxonomy_entries))
print("labels still missing", missing_labels)
print(len(missing_labels))

########
# Inconsistency Checks
#######
# creating a excel file and then manually controlling it

to_check = []
# looping twice to get pair of each
for index, row in data.iterrows():
    for index_, row_ in data.iterrows():
        if row["title"] == row_["title"] and row["labels"] != row_["labels"]:
            to_check.append(row)

for index, row in data.iterrows():
    if row["description"] != "None" and row["description"] != "NONE":
        for indexing, rowing in data.iterrows():
            if (
                row["description"] == rowing["description"]
                and row["labels"] != rowing["labels"]
            ):
                to_check.append(row)

to_check_df = pd.DataFrame(to_check)
to_check_df.to_excel(
    "data/processed/check_ambiguous_same_description.xlsx", index=False
)

########
# Identify new categories with Sonstiges
#######

sonstiges_list = []

for index, row in data.iterrows():
    if row["labels_name"] == "Sonstiges - Sonstiges":
        sonstiges_list.append(row)

sonstiges_df = pd.DataFrame(sonstiges_list)
sonstiges_df.to_excel("data/processed/sonstiges_categories.xlsx", index=False)


#######
# Auto und Schwerlastenverkehr - Examples
#######

auto_schwerlast = (
    data[["labels_name"]]
    .apply(lambda x: x.str.contains("Auto und Schwerlastverkehr", regex=True))
    .any(axis=1)
)

examples_auto_schwerlast = data[auto_schwerlast]
examples_auto_schwerlast.to_excel(
    "data/processed/examples_auto_schwerlast.xlsx", index=False
)

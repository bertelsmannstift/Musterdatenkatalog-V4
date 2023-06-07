"""
generates annotation data for annotation tool
"""
import uuid

import pandas as pd

from src.settings import Settings


def get_necessary_variables(df: pd.DataFrame) -> pd.DataFrame:
    return df[["MUSTERDATENSATZ", "dct:title", "dct:description"]]


def generate_uuid(df: pd.DataFrame) -> pd.DataFrame:
    df["uuid"] = [uuid.uuid4() for _ in range(len(df.index))]
    return df


if __name__ == "__main__":
    # Load Data
    settings = Settings(_env_file="paths/.env.dev")
    df_gov_data = pd.read_csv(
        "data/raw/2022-12-15_gov_meta_data_sets_per_category.csv"
    )  # change depending on date
    df_baseline_mdk_training_data = pd.read_csv(
        settings.BASELINE_MDK_TRAINING_DATA_PROCESSED_V2
    )
    df_baseline_mdk_enriched_data = pd.read_csv(settings.BASELINE_MDK_ENRICHED_DATA)

    # Preprocess Training Data
    df_baseline_mdk_training_data = get_necessary_variables(
        df=df_baseline_mdk_training_data
    )

    df_baseline_mdk_training_data = generate_uuid(df=df_baseline_mdk_training_data)

    frequency_baseline_mdk_training_data = (
        df_baseline_mdk_training_data.groupby("MUSTERDATENSATZ")
        .size()
        .reset_index(name="count")
    )

    frequency_baseline_mdk_training_data_more_than_5_examples_mdks = (
        frequency_baseline_mdk_training_data[
            frequency_baseline_mdk_training_data["count"] >= 3
        ]["MUSTERDATENSATZ"].tolist()
    )

    frequency_baseline_mdk_training_data_less_than_5_examples_mdks = (
        frequency_baseline_mdk_training_data[
            frequency_baseline_mdk_training_data["count"] < 3
        ]["MUSTERDATENSATZ"].tolist()
    )

    frequency_baseline_mdk_training_data_more_than_5_examples = (
        df_baseline_mdk_training_data[
            df_baseline_mdk_training_data["MUSTERDATENSATZ"].isin(
                frequency_baseline_mdk_training_data_more_than_5_examples_mdks
            )
        ]
    )

    frequency_baseline_mdk_training_data_less_than_5_examples = (
        df_baseline_mdk_training_data[
            df_baseline_mdk_training_data["MUSTERDATENSATZ"].isin(
                frequency_baseline_mdk_training_data_less_than_5_examples_mdks
            )
        ]
    )

    frequency_baseline_mdk_training_data_more_than_5_examples_sample = (
        frequency_baseline_mdk_training_data_more_than_5_examples.groupby(
            "MUSTERDATENSATZ"
        ).sample(n=3)
    )

    df_baseline_mdk_training_data_sample = pd.concat(
        [
            frequency_baseline_mdk_training_data_more_than_5_examples_sample,
            frequency_baseline_mdk_training_data_less_than_5_examples,
        ]
    )

    df_baseline_mdk_training_data_sample = df_baseline_mdk_training_data_sample[
        df_baseline_mdk_training_data_sample["MUSTERDATENSATZ"] != "None"
    ]

    # Preprocess Enriched Data
    df_baseline_mdk_enriched_data = pd.read_csv(settings.BASELINE_MDK_ENRICHED_DATA)

    # Preprocess Training Data
    df_baseline_mdk_enriched_data = get_necessary_variables(
        df=df_baseline_mdk_enriched_data
    )

    df_baseline_mdk_enriched_data = generate_uuid(df=df_baseline_mdk_enriched_data)

    df_baseline_mdk_enriched_data_sample = df_baseline_mdk_enriched_data.groupby(
        "MUSTERDATENSATZ"
    ).sample(frac=0.025)

    # preprocess Gov data
    df_gov_data = generate_uuid(df=df_gov_data)
    df_gov_data["MUSTERDATENSATZ"] = ["None" for _ in range(len(df_gov_data.index))]
    df_gov_data = df_gov_data[
        ["MUSTERDATENSATZ", "dct:title", "dct:description", "uuid"]
    ]

    df_gov_data = df_gov_data.sample(frac=1)

    df_gov_data_sample = df_gov_data.sample(n=250)

    # concatenate all datasets
    annotation_sample = pd.concat(
        [
            df_gov_data_sample,
            df_baseline_mdk_enriched_data_sample,
            df_baseline_mdk_training_data_sample,
        ]
    )

    annotation_sample = annotation_sample.fillna(value="None")

    annotation_sample["title_and_description"] = annotation_sample[
        ["dct:title", "dct:description"]
    ].agg("  STOP TITLE START DESCRIPTION ".join, axis=1)

    annotation_sample["text"] = annotation_sample[
        ["title_and_description", "MUSTERDATENSATZ"]
    ].agg(" STOP DESCRIPTION START MUSTERDATENSATZ ".join, axis=1)

    annotation_sample = annotation_sample.sample(frac=1)

    # CODE for getting Round 1 Sample
    """
    This code would generate the first round samples. Since some
    issues during the annotation process
    the data for the round 1 was separately generated.
    In order to ensure that there are no duplicates
    with the other annotation rounds round 1 is loaded into the script
    and all documents of the
    other rounds are checked against the documents of round 1.

    round_1_sample = annotation_sample[:100]  # length 50
    round_1_sample_Rater_1_individual = round_1_sample[:40]
    round_1_sample_Rater_2_individual = round_1_sample[40:80]
    round_1_sample_co_assignment = round_1_sample[80:]

    round_1_sample_Rater_1 = pd.concat(
        [round_1_sample_Rater_1_individual, round_1_sample_co_assignment]
    )
    round_1_sample_Rater_2 = pd.concat(
        [round_1_sample_Rater_2_individual, round_1_sample_co_assignment]
    )

    round_1_sample_Rater_1.to_csv(
        path_or_buf="data/annotations/Round_01/Tasks/round_1_rater_1.csv"
    )
    round_1_sample_Rater_2.to_csv(
        path_or_buf="data/annotations/Round_01/Tasks/round_1_rater_2.csv"
    )
    """

    # CODE TO GET round_1 Sample Data
    round_1_rater_1 = pd.read_csv(
        filepath_or_buffer="data/annotations/Round_01/Tasks/round_1_rater_1.csv"
    )
    round_1_rater_2 = pd.read_csv(
        filepath_or_buffer="data/annotations/Round_01/Tasks/round_1_rater_2.csv"
    )

    round_1_sample = pd.concat([round_1_rater_1, round_1_rater_2])

    texts = round_1_sample["dct:title"].tolist()

    annotation_sample_without_round_1 = annotation_sample[
        ~annotation_sample["dct:title"].isin(texts)
    ]

    # Round 2
    round_2_sample = annotation_sample_without_round_1[100:400]
    # Round 3
    round_3_sample = annotation_sample_without_round_1[400:700]  # length 300

    # Round 4
    round_4_sample = annotation_sample_without_round_1[700:]  # length 416

    round_2_sample.to_csv(
        path_or_buf="data/annotations/round_2_sample.csv", index=False
    )
    round_3_sample.to_csv(
        path_or_buf="data/annotations/round_3_sample.csv", index=False
    )
    round_4_sample.to_csv(
        path_or_buf="data/annotations/round_4_sample.csv", index=False
    )

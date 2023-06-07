"""Split the annotation sample in batches and for each rater"""

from typing import List

import pandas as pd

from src.settings import Settings


def check_duplicates(texts: List, df: pd.DataFrame) -> None:
    """checks if there is any duplicates between the data.

    Parameters
    ----------
    texts : List
        validation titles
    df : pd.DataFrame
        data to checked

    Raises
    ------
    ValueError
        duplicates found between the data to be checked and other rounds
    """
    if len(set(texts).intersection(df["dct:title"].tolist())) == 0:
        print("no duplicates")
    else:
        print(set(texts).intersection(df["dct:title"].tolist()))
        raise ValueError("Duplicates found!")


def distribute_data(
    data: pd.DataFrame, rater_number: int, co_assignment: int
) -> List[pd.DataFrame]:
    """distributes the data to raters with co_assignment

    Parameters
    ----------
    data : pd.DataFrame
        data for annotation
    rater_number : int
        number of raters for annotation round
    co_assignment : int
        number of co_assignment data

    Returns
    -------
    List[pd.DataFrame]
        distributed data where each element in the list represents one rater
    """
    splitted_data = []
    data_length = len(data)
    individual_data_length = int((data_length - co_assignment) / rater_number)
    co_assignment_data = data[data_length - co_assignment :]  # noqa: E203
    individual_data_length_per_rater = 0
    for _ in range(0, rater_number):
        current_rater_data = data[
            individual_data_length_per_rater : (  # noqa: E203
                individual_data_length_per_rater + individual_data_length
            )
        ]
        individual_data_length_per_rater = (
            individual_data_length_per_rater + individual_data_length
        )
        splitted_data.append(pd.concat([current_rater_data, co_assignment_data]))

    return splitted_data


if __name__ == "__main__":
    settings = Settings(_env_file="paths/.env.dev")

    OUTPUT_BASE_PATH = str(settings.BASE_PATH_ANNOTATIONS_ROUNDS)
    SAMPLE_BASE_PATH = str(settings.BASE_PATH_ANNOTATIONS)
    ROUND = "4"
    # read data (round_1 was created manually,
    # which is why we check against all texts of
    # round 1 to avoid duplicates between
    # the annotation rounds)
    round_1_rater_1 = pd.read_csv(
        filepath_or_buffer=f"{SAMPLE_BASE_PATH}/round_1_rater_1.csv"
    )
    round_1_rater_2 = pd.read_csv(
        filepath_or_buffer=f"{SAMPLE_BASE_PATH}/round_1_rater_2.csv"
    )

    round_1_sample = pd.concat([round_1_rater_1, round_1_rater_2])

    texts = round_1_sample["dct:title"].tolist()

    # Create round
    # read data
    sample = pd.read_csv(
        filepath_or_buffer=f"{SAMPLE_BASE_PATH}/round_{ROUND}_sample.csv"
    )

    # check against round 1 data
    check_duplicates(texts=texts, df=sample)

    # splitting
    splitting = distribute_data(data=sample, rater_number=2, co_assignment=58)

    for idx, split in enumerate(splitting):
        split.to_csv(
            f"{OUTPUT_BASE_PATH}_0{ROUND}/round_{ROUND}_rater_{idx+1}.csv", index=False
        )

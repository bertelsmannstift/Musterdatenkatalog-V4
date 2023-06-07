"""fine tuning BERT based on siamese network architecture.
This file is to regenerate the model with revision a907303609264155e704988a4e52dd07f169538f.

This revision of the model is then used for retraining the bi encoder model which is the current version on huggingface hub.

"""  # noqa: E501

import logging
import os
import random
from typing import Dict, List, Tuple, Union

import pandas as pd
from dotenv import load_dotenv
from huggingface_hub import HfApi, snapshot_download
from sentence_transformers import InputExample, SentenceTransformer, losses, util
from torch.utils.data import DataLoader

from src.settings import Settings

settings = Settings(_env_file="paths/.env.dev")

dotenv_path = ".env"
load_dotenv(dotenv_path)

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


class SentenceTransformerTrainer:
    """fine tuning bert for skills"""

    def __init__(self) -> None:
        self.max_seq_length: Union[int, None] = None
        self.model: SentenceTransformer = None
        self.train_args: Dict = {}

    def parse_to_dataloader(self, data: pd.DataFrame, type_of_data: str) -> DataLoader:
        """create pairs for similar and unsimilar data
        similar pairs: (title, corresponding label name) | (title, corresponding group name)
        unsimilar pairs: (title, other label than corresponding), 2 examples

        Parameters
        ----------
        data : pd.DataFrame
            training data

        Returns
        -------
        DataLoader
            examples of similar and unsimilar pairs
        """
        if type_of_data == "train":
            similar_pairs_size = "train_similar_pair_size"
            unsimilar_pairs_size = "train_unsimilar_pair_size"
            total_pair_size = "train_total_size"
        else:
            similar_pairs_size = "test_similar_pair_size"
            unsimilar_pairs_size = "test_unsimilar_pair_size"
            total_pair_size = "test_total_size"

        titles_per_class = data.groupby(by="labels_name")["title"].apply(list).to_dict()
        data["group"] = data.apply(
            lambda x: x["labels_name"].split("-", 1)[0].rstrip(), axis=1
        )
        titles_per_group = data.groupby(by="group")["title"].apply(list).to_dict()

        similar_examples = [
            InputExample(texts=[category, title], label=0.8)
            for category, titles in titles_per_class.items()
            for title in titles
        ]

        for group, titles in titles_per_group.items():
            for title in titles:
                similar_examples.append(InputExample(texts=[group, title], label=0.8))

        self.train_args[similar_pairs_size] = len(similar_examples)
        logger.info(msg=f"Number of similar pairs: {len(similar_examples)}")

        unsimilar_examples: List = []
        categories = list(titles_per_class.keys())

        for current_category, titles in titles_per_class.items():
            for title in titles:
                pairs = [
                    InputExample(texts=[category, title], label=0.2)
                    for category in categories
                    if category != current_category
                ]
                for el in random.sample(population=pairs, k=1):
                    unsimilar_examples.append(el)

        self.train_args[unsimilar_pairs_size] = len(unsimilar_examples)
        logger.info(msg=f"Number of unsimilar pairs: {len(unsimilar_examples)}")

        examples = similar_examples + unsimilar_examples

        self.train_args[total_pair_size] = len(examples)
        logger.info(msg=f"Length of dataloader: {len(examples)}")

        dataloader = DataLoader(examples, shuffle=True, batch_size=16)
        return dataloader

    def _load_model(
        self, max_seq_length: int, model_name: str, revision: Union[str, None] = None
    ):
        """loads bert model

        Parameters
        ----------
        max_seq_length : int
            maximal length of a sequence
        model_name : str
            name of base model
        """
        logger.info(msg="Load Model")
        if revision is not None:
            path = snapshot_download(
                repo_id=model_name, revision=revision, repo_type="model", token=True
            )
            self.model = SentenceTransformer(path)
        else:
            self.max_seq_length = max_seq_length
            self.model = SentenceTransformer(model_name)

    def train(
        self,
        data: DataLoader,
        epochs: int,
        warmup_steps: int,
        max_seq_length: int,
        model_name: str,
        train=True,
        revision=Union[str, None],
    ) -> None:
        """fine tune bert

        Parameters
        ----------
        data : DataLoader
            trainingsdata
        epochs : int
            epochs for training
        warmup_steps : int
            warumup steps for training
        max_seq_length : int
            maximal sequence length
        model_name : str
            base model name
        """
        logger.info(msg="*****MODEL TRAINING*****")
        self.train_args["epochs"] = epochs
        self.train_args["warmup_steps"] = warmup_steps
        if revision:
            self._load_model(
                max_seq_length=max_seq_length, model_name=model_name, revision=revision
            )
        else:
            self._load_model(max_seq_length=max_seq_length, model_name=model_name)
        train_loss = losses.CosineSimilarityLoss(self.model)
        if train:
            self.model.fit(
                train_objectives=[(data, train_loss)],
                epochs=epochs,
                warmup_steps=warmup_steps,
            )

    def evaluate(self, data: DataLoader) -> Tuple[List, List]:
        """evaluation of fine tuning: calculate the difference between
        base values 0.8 (similar) and 0.2(unsimilar) with predicted similarity

        Parameters
        ----------
        data : DataLoader
            test data

        Returns
        -------
        Tuple[List, List]
            predictions for similar and unsimilar testing
        """
        logger.info(msg="*****MODEL EVALUATION*****")
        predictions_similar: List = []
        predicitions_unsimilar: List = []
        for el in data.dataset:
            label: float = el.label
            pair: Tuple = el.texts
            sim = util.cos_sim(
                a=self.model.encode(pair[0]), b=self.model.encode(pair[1])
            ).item()
            if label == 0.8:
                predictions_similar.append(abs(sim - 0.8))
            if label == 0.2:
                predicitions_unsimilar.append(abs(sim - 0.2))
        predictions_similar_mean = sum(predictions_similar) / len(predictions_similar)
        predicitions_unsimilar_mean = sum(predicitions_unsimilar) / len(
            predicitions_unsimilar
        )

        logger.info(msg=f"Average similarity similar pairs {predictions_similar_mean}")
        logger.info(
            msg=f"Average similarity unsimilar pairs {predicitions_unsimilar_mean}"
        )

        return predictions_similar, predicitions_unsimilar

    @staticmethod
    def push_to_hub(output_path: str, commit_message: str):
        """push model to huggingface hub

        Parameters
        ----------
        output_path : str
            path to model
        commit_message : str
            commit message
        """
        hf_api = HfApi()
        hf_api.upload_folder(
            folder_path=output_path,
            path_in_repo="",
            repo_id="and-effect/musterdatenkatalog_clf",
            repo_type="model",
            commit_message=commit_message,
            token=os.environ.get("HF_TOKEN"),
        )

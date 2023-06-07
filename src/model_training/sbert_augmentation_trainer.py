"""
This class is for training a bi encoder with SBERT Augmentation.
"""

import logging
import math
import os
import random
from typing import Dict, List, Tuple, Union

import pandas as pd
import torch
import tqdm
from dotenv import load_dotenv
from huggingface_hub import snapshot_download
from sentence_transformers import InputExample, SentenceTransformer, util
from sentence_transformers.cross_encoder import CrossEncoder
from sentence_transformers.cross_encoder.evaluation import CECorrelationEvaluator
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


class SBERTAugmentationTrainer:
    """fine tuning bert for skills"""

    def __init__(self) -> None:
        self.cross_encoder: CrossEncoder = None
        self.semantic_model: SentenceTransformer = None
        self.train_args: Dict = {}
        self.gold_samples: List[InputExample] = []
        self.dev_samples: List[InputExample] = []
        self.silver_data: List = []

    def _load_cross_encoder(self, model_name: str):
        """loads Cross Encoder Model

        Parameters
        ----------
        model_name : str
            name of base model
        """
        logger.info(msg="Load Model")

        self.cross_encoder = CrossEncoder(model_name=model_name)

    def _load_semantic_search_model(
        self, model_name: str, revision: Union[str, None]
    ) -> None:
        """loads semantic search model

        Parameters
        ----------
        model_name : str
            name of model
        revision : Union[str, None]
            revision of model, by default None
        """
        if revision:
            path = snapshot_download(
                repo_id=model_name, revision=revision, repo_type="model", token=True
            )

            self.semantic_model = SentenceTransformer(path)
        else:
            self.semantic_model = SentenceTransformer(model_name)

    def parse_samples(
        self, training_data: pd.DataFrame, dev_data: pd.DataFrame
    ) -> Tuple[DataLoader, CECorrelationEvaluator]:
        """create pairs for similar and unsimilar data for the cross encoder model

        Parameters
        ----------
        training_data : pd.DataFrame
            labelled training data
        dev_data : pd.DataFrame
            labelled dev/test data

        Returns
        -------
        Tuple[DataLoader, CECorrelationEvaluator]:
            dataloader for training with gold samples and evaluation

        """
        titles_per_category = (
            training_data.groupby(by=["labels_name"])["title"].apply(list).to_dict()
        )

        categories = list(training_data["labels_name"].unique())

        for current_category, titles in titles_per_category.items():
            for title in titles:
                self.gold_samples.append(
                    InputExample(texts=[title, current_category], label=0.8)
                )
                unsimilar_temp = [
                    InputExample(texts=[title, category], label=0.2)
                    for category in categories
                    if current_category != category
                ]
                for el in random.sample(unsimilar_temp, 1):
                    self.gold_samples.append(el)

        titles_per_category = (
            dev_data.groupby(by=["labels_name"])["title"].apply(list).to_dict()
        )
        categories = list(dev_data["labels_name"].unique())

        for current_category, titles in titles_per_category.items():
            for title in titles:
                self.dev_samples.append(
                    InputExample(texts=[title, current_category], label=0.8)
                )
                unsimilar_temp = [
                    InputExample(texts=[title, category], label=0.2)
                    for category in categories
                    if current_category != category
                ]
                for el in random.sample(unsimilar_temp, 1):
                    self.dev_samples.append(el)

        train_dataloader = DataLoader(self.gold_samples, shuffle=True, batch_size=16)

        evaluator = CECorrelationEvaluator.from_input_examples(
            self.dev_samples, name="sts-dev"
        )

        return train_dataloader, evaluator

    def _train_model(
        self,
        train_dataloader: DataLoader,
        evaluator: CECorrelationEvaluator,
        num_epochs: int,
    ):
        """This function trains the cross encoder model

        Parameters
        ----------
        train_dataloader : DataLoader
            dataloader for training
        evaluator : CECorrelationEvaluator
            evaluator for evaluation
        num_epochs : int
            number of epochs
        """
        logger.info(msg="Start Training")
        warmup_steps = math.ceil(len(train_dataloader) * num_epochs * 0.1)

        self.cross_encoder.fit(
            train_dataloader=train_dataloader,
            evaluator=evaluator,
            epochs=num_epochs,
            evaluation_steps=1000,
            warmup_steps=warmup_steps,
        )

    def augment_data(
        self,
        trainings_data_loader: DataLoader,
        evaluator: CECorrelationEvaluator,
        cross_encoder_base_model: str,
        semantic_search_model: str,
        semantic_search_model_revision: Union[str, None],
    ) -> DataLoader:
        """augment data with SBERT

        Parameters
        ----------
        trainings_data_loader : DataLoader
            dataloader for training
        evaluator : CECorrelationEvaluator
            evaluator for evaluation
        cross_encoder_base_model : str
            base model
        semantic_search_model : str
            semantic search model for getting sentence pairs
        semantic_search_model_revision : Union[str, None]
            revision of semantic search model, by default None

        Returns
        -------
        DataLoader
            dataloader with augmented data
        """
        logger.info("load cross encoder")
        self._load_cross_encoder(model_name=cross_encoder_base_model)

        logger.info("load semantic search model")
        self._load_semantic_search_model(
            model_name=semantic_search_model, revision=semantic_search_model_revision
        )

        logger.info("prepare data for augmentation")
        sentences = set()

        for sample in self.gold_samples:
            sentences.update(sample.texts)

        sentences = list(sentences)
        sent2idx = {
            sentence: idx for idx, sentence in enumerate(sentences)
        }  # storing id and sentence in dictionary

        duplicates = set(
            (sent2idx[data.texts[0]], sent2idx[data.texts[1]])
            for data in self.gold_samples
        )  # not to include gold pairs of sentences agains

        # Use the current bi-encoder to encode all sentences
        embeddings = self.semantic_model.encode(
            sentences, batch_size=16, convert_to_tensor=True
        )

        logger.info("get sentences")
        progress = tqdm.tqdm(unit="docs", total=len(sent2idx))
        for idx in range(len(sentences)):
            sentence_embedding = embeddings[idx]
            cos_scores = util.cos_sim(sentence_embedding, embeddings)[0]
            cos_scores = cos_scores.cpu()
            progress.update(1)

            top_results = torch.topk(cos_scores, k=3 + 1)

            for score, iid in zip(top_results[0], top_results[1]):
                if iid != idx and (iid, idx) not in duplicates:
                    self.silver_data.append((sentences[idx], sentences[iid]))
                    duplicates.add((idx, iid))
        progress.reset()
        progress.close()

        logger.info("Train cross encoder")
        self._train_model(
            train_dataloader=trainings_data_loader, evaluator=evaluator, num_epochs=3
        )

        silver_scores = self.cross_encoder.predict(self.silver_data)

        assert all(0.0 <= score <= 1.0 for score in silver_scores)

        logger.info("Score Silver Data")
        silver_samples = list(
            InputExample(texts=[data[0], data[1]], label=score)
            for data, score in zip(self.silver_data, silver_scores)
        )

        silver_sample_loader = DataLoader(silver_samples, shuffle=True, batch_size=16)

        return silver_sample_loader

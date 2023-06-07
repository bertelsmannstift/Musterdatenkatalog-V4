"""Pipeline Component: classifies each title
of parsed data from parser.py.
Provides also evaluation measurements"""

from typing import Dict, List

import torch
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score


class BertSim:
    """Cosine Similarity based Text Classification"""

    def __init__(self, model: SentenceTransformer, corpus: List) -> None:
        self.model = SentenceTransformer(model_name_or_path=model)
        self.corpus: List = corpus
        self.corpus_embeddings: torch.Tensor
        self._load_corpus()

    def _load_corpus(self) -> None:
        """loads the corpus and embeds it"""
        self.corpus_embeddings = self.model.encode(self.corpus, convert_to_tensor=True)
        self.corpus_embeddings = util.normalize_embeddings(self.corpus_embeddings)

    def predict(self, queries: List) -> List[Dict]:
        """predict for an input sentence based a label of the corpus

        Parameters
        ----------
        queries : List
            input query or queries

        Returns
        -------
        List[Dict]
            results with the query text, the predicted label from the corpus
            and the cosine similarity score
        """
        query_embeddings = self.model.encode(
            sentences=queries, convert_to_tensor=True, show_progress_bar=False
        )
        query_embeddings = util.normalize_embeddings(query_embeddings)
        semantic_search_results = util.semantic_search(
            query_embeddings=query_embeddings,
            corpus_embeddings=self.corpus_embeddings,
            top_k=1,
        )
        results = [
            {
                "text": queries[idx],
                "prediction": self.corpus[el[0]["corpus_id"]],
                "score": el[0]["score"],
            }
            for idx, el in enumerate(semantic_search_results)
        ]

        return results

    def classification_report_macro(
        self,
        predictions: List,
        docs_true_labels: List,
        exclude_not_predicted: int = 0,
        corpus: List = [],
    ) -> Dict:
        """generates a classification report (macro) with accuracy,
         precision, recall and f1

        Parameters
        ----------
        predictions : List
            labels predictions of model
        docs_true_labels : List
            true labels
        exclude_not_predicted : int, optional
            if zero all precision, recall and f1 are calculatd for all classes, if set to a certain number all labels which have lower predictions than this number are excluded, by default 0
        corpus : list, optional
            if exclude_not_predicted, need to be filled. Should include all categories, by default []

        Returns
        -------
        _type_
            _description_
        """
        accuracy = accuracy_score(y_true=docs_true_labels, y_pred=predictions)
        if exclude_not_predicted > 0:
            examples_per_category = {x: predictions.count(x) for x in predictions}
            predicted_labels = list(
                set(
                    [
                        key
                        for key, value in examples_per_category.items()
                        if value >= exclude_not_predicted
                    ]
                )
            )
            precision = precision_score(
                y_true=docs_true_labels,
                y_pred=predictions,
                average="macro",
                labels=predicted_labels,
            )
            recall = recall_score(
                y_true=docs_true_labels,
                y_pred=predictions,
                average="macro",
                labels=predicted_labels,
            )
            f1 = f1_score(
                y_true=docs_true_labels,
                y_pred=predictions,
                average="macro",
                labels=predicted_labels,
            )
            print(
                f"Percentage of predicted labels: {len(set(predicted_labels)) / len(set(corpus)) * 100}"  # noqa: E501
            )
            print(
                f"Percentage of predicted labels (true labels): {len(set(predicted_labels)) / len(set(docs_true_labels)) * 100}"  # noqa: E501
            )
        else:
            precision = precision_score(
                y_true=docs_true_labels,
                y_pred=predictions,
                average="macro",
            )
            recall = recall_score(
                y_true=docs_true_labels,
                y_pred=predictions,
                average="macro",
            )
            f1 = f1_score(
                y_true=docs_true_labels,
                y_pred=predictions,
                average="macro",
            )
        return {
            "accuracy": accuracy,
            "precision_macro": precision,
            "recall_macro": recall,
            "f1_macro": f1,
        }

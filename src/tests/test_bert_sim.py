from typing import Dict, List, Union

import pytest
from sklearn.metrics.pairwise import cosine_similarity

from src.components.bert_sim import BertSim
from src.settings import Settings
from src.utils.data import load_json


def test_bert_sim(model, taxonomy: Union[List, Dict]) -> None:
    """pytest for BertSim class for text classification with one test case"""
    corpus = [concept["group"] + " - " + concept["label"] for concept in taxonomy]

    bert_sim = BertSim(model=model, corpus=corpus)
    query_list = [
        "Justiz - Gesetzestext",
    ]
    prediction = bert_sim.predict(queries=query_list)

    # model encoding correct if same prediction made
    all_label_embedding = bert_sim.model.encode(corpus)
    label_embedding = [all_label_embedding[corpus.index(i)] for i in query_list]
    input_embedding = bert_sim.model.encode(prediction)

    assert len(label_embedding) == len(input_embedding) == 1

    assert cosine_similarity(
        [label_embedding][0], [input_embedding][0]
    ) == pytest.approx(1.0)


if __name__ == "__main__":
    settings = Settings(_env_file="paths/.env.dev")
    model = "bert-base-german-cased"
    taxonomy = load_json(settings.TAXONOMY_PROCESSED_V2)
    test_bert_sim(model, taxonomy)

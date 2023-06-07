"""
This is the training script for the model with revision a907303609264155e704988a4e52dd07f169538f
on huggingface hub.
The output of this model is used for retraining the bi encoder model with SBERT Augementation.
"""


from typing import Dict

from datasets import load_dataset
from huggingface_hub import HfApi

from src.model_training.sentence_transfomer_trainer import SentenceTransformerTrainer

MAX_SEQ_LENGTH = 256
EPOCHS = 4
WARUMUP_STEPS = 100
DATA_PATH = "and-effect/mdk_gov_data_titles_clf"
BASE_MODEL_NAME = "dbmdz/bert-base-german-cased"
OUTPUT_PATH = "models/bi_encoder_model_revision_a90730"


model_card_parameters: Dict = {"card_data": {}, "content": {}}

revision = "172e61bb1dd20e43903f4c51e5cbec61ec9ae6e6"  # pragma: allowlist secret

# Load Data
data = load_dataset(
    DATA_PATH,
    data_dir="large",
    use_auth_token=True,
    revision=revision,
)

# Preprocess Data
current_data_train = data["train"].to_pandas()


hf_api = HfApi()
data_sha = hf_api.dataset_info(
    "and-effect/mdk_gov_data_titles_clf", revision=revision
).sha[:7]

trainer = SentenceTransformerTrainer()

train_dataloader = trainer.parse_to_dataloader(
    data=current_data_train, type_of_data="train"
)

test_dataloader = trainer.parse_to_dataloader(
    data=data["test"].to_pandas(), type_of_data="test"
)

trainer.train(
    data=train_dataloader,
    epochs=EPOCHS,
    warmup_steps=WARUMUP_STEPS,
    max_seq_length=MAX_SEQ_LENGTH,
    model_name=BASE_MODEL_NAME,
    revision=None,
)

trainer.model.save(OUTPUT_PATH)

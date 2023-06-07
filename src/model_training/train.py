"""
This is the training script for the current version of
the bi encoder model on huggingface hub.
We uploaded the model manually to huggingface hub.
"""

from datasets import load_dataset

from src.model_training.sbert_augmentation_trainer import SBERTAugmentationTrainer
from src.model_training.sentence_transfomer_trainer import SentenceTransformerTrainer

EPOCHS = 3
WARUMUP_STEPS = 100
DATA_PATH = "and-effect/mdk_gov_data_titles_clf"
SEMANTIC_SEARCH_MODEL = "and-effect/musterdatenkatalog_clf"
SEMANTIC_SEARCH_MODEL_REVISION = (
    "a907303609264155e704988a4e52dd07f169538f"  # pragma: allowlist secret
)
BI_ENCODER_BASE_MODEL = "and-effect/musterdatenkatalog_clf"
BI_ENCODER_BASE_MODEL_REVISION = (
    "a907303609264155e704988a4e52dd07f169538f"  # pragma: allowlist secret
)
CROSS_ENCODER_BASE_MODEL = "bert-base-german-cased"
OUTPUT_PATH = "models/bi_encoder_model"
COMMIT_MESSAGE = "bi encoder model trained with SBERT Augmentation"


data = load_dataset(
    DATA_PATH,
    data_dir="large",
    use_auth_token=True,
)

# Preprocess Data
training_data = data["train"].to_pandas()[:50]
dev_data = data["test"].to_pandas()[:20]

augementation_trainer = SBERTAugmentationTrainer()

# get samples
training_data_loader, evaluator = augementation_trainer.parse_samples(
    training_data=training_data, dev_data=dev_data
)

# augment data
silver_sample_loader = augementation_trainer.augment_data(
    trainings_data_loader=training_data_loader,
    evaluator=evaluator,
    cross_encoder_base_model=CROSS_ENCODER_BASE_MODEL,
    semantic_search_model=SEMANTIC_SEARCH_MODEL,
    semantic_search_model_revision=SEMANTIC_SEARCH_MODEL_REVISION,
)

# train bi encoder model
bi_encoder_trainer = SentenceTransformerTrainer()

bi_encoder_trainer.train(
    data=silver_sample_loader,
    epochs=EPOCHS,
    warmup_steps=WARUMUP_STEPS,
    max_seq_length=256,
    model_name=BI_ENCODER_BASE_MODEL,
    revision=BI_ENCODER_BASE_MODEL_REVISION,
)

bi_encoder_trainer.model.save(OUTPUT_PATH)

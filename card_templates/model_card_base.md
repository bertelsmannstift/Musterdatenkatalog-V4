---
# For reference on model card metadata, see the spec: https://github.com/huggingface/hub-docs/blob/main/modelcard.md?plain=1
# Doc / guide: https://huggingface.co/docs/hub/model-cards
{{ card_data }}
---

# Model Card for Musterdatenkatalog Classifier

# Model Details

## Model Description

{{ model_description | default("[More Information Needed]", true) }}

- **Developed by:** and-effect
- **Shared by:** {{ shared_by | default("[More Information Needed]", true)}}
- **Model type:** Text Classification
- **Language(s) (NLP):** de
- **License:** {{ license | default("[More Information Needed]", true)}}
- **Finetuned from model:** "bert-base-german-case. For more information one the model check on [this model card](https://huggingface.co/bert-base-german-cased)"

## Model Sources

<!-- Provide the basic links for the model. -->

- **Repository:** {{ repo | default("[More Information Needed]", true)}}
- **Paper:** {{ paper | default("[More Information Needed]", true)}}
- **Demo:** {{ demo | default("[More Information Needed]", true)}}

# Direct Use

This is a [sentence-transformers](https://www.SBERT.net) model: It maps sentences & paragraphs to a 768 dimensional dense vector space and can be used for tasks like clustering or semantic search.

## Get Started with Sentence Transformers

Using this model becomes easy when you have [sentence-transformers](https://www.SBERT.net) installed:

```
pip install -U sentence-transformers
```

Then you can use the model like this:

```python
from sentence_transformers import SentenceTransformer
sentences = ["This is an example sentence", "Each sentence is converted"]

model = SentenceTransformer('{MODEL_NAME}')
embeddings = model.encode(sentences)
print(embeddings)
```

## Get Started with HuggingFace Transformers

Without [sentence-transformers](https://www.SBERT.net), you can use the model like this: First, you pass your input through the transformer model, then you have to apply the right pooling-operation on-top of the contextualized word embeddings.

```python
from transformers import AutoTokenizer, AutoModel
import torch


#Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


# Sentences we want sentence embeddings for
sentences = ['This is an example sentence', 'Each sentence is converted']

# Load model from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained('{MODEL_NAME}')
model = AutoModel.from_pretrained('{MODEL_NAME}')

# Tokenize sentences
encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

# Compute token embeddings
with torch.no_grad():
    model_output = model(**encoded_input)

# Perform pooling. In this case, mean pooling.
sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

print("Sentence embeddings:")
print(sentence_embeddings)
```

# Downstream Use

<!-- This section is for the model use when fine-tuned for a task, or when plugged into a larger ecosystem/app -->

The model is intended to classify open source dataset titles from german municipalities. More information on the Taxonomy (classification categories) and the Project can be found on XY.

{{ downstream_use_demo | default("[More Information Needed on downstream_use_demo]", true)}}

# Bias, Risks, and Limitations

<!-- This section is meant to convey both technical and sociotechnical limitations. -->

The model has some limititations. The model has some limitations in terms of the downstream task. \n 1. **Distribution of classes**: The dataset trained on is small, but at the same time the number of classes is very high. Thus, for some classes there are only a few examples (more information about the class distribution of the training data can be found here). Consequently, the performance for smaller classes may not be as good as for the majority classes. Accordingly, the evaluation is also limited. \n 2. **Systematic problems**: some subjects could not be correctly classified systematically. One example is the embedding of titles containing 'Corona'. In none of the evaluation cases could the titles be embedded in such a way that they corresponded to their true names. Another systematic example is the embedding and classification of titles related to 'migration'. \n 3. **Generalization of the model**: by using semantic search, the model is able to classify titles into new categories that have not been trained, but the model is not tuned for this and therefore the performance of the model for unseen classes is likely to be limited.

## Recommendations

<!-- This section is meant to convey recommendations with respect to the bias, risk, and technical limitations. -->

{{ bias_recommendations | default("Users (both direct and downstream) should be made aware of the risks, biases and limitations of the model. More information needed for further recommendations.", true)}}

# Training Details

## Training Data

<!-- This should link to a Data Card, perhaps with a short stub of information on what the training data is all about as well as documentation related to data pre-processing or additional filtering. -->

{{ training_data | default("[More Information Needed]", true)}}

## Training Procedure

### Preprocessing

This section describes the generating of the input data for the model. More information on the preprocessing of the data itself can be found [here](https://huggingface.co/datasets/and-effect/mdk_gov_data_titles_clf)

The model is fine tuned with similar and dissimilar pairs. Similar pairs are built with all titles and their true label. Dissimilar pairs defined as pairs of title and all labels, except the true label. Since the combinations of dissimilar is much higher, a sample of two pairs per title is selected.

{{ overview_pairs | default("[More Information Needed]", true)}}

## Training Parameter

The model was trained with the parameters:

**DataLoader**:
`torch.utils.data.dataloader.DataLoader`

**Loss**:
`sentence_transformers.losses.CosineSimilarityLoss.CosineSimilarityLoss`

Hyperparameter:

```
{
    "epochs": {{ epochs | default("[More Information Needed]", true) }},
    "warmup_steps": {{ warmup_steps | default("[More Information Needed]", true) }},
}
```

### Speeds, Sizes, Times

<!-- This section provides information about throughput, start/end time, checkpoint size if relevant, etc. -->

{{ speeds_sizes_times | default("[More Information Needed]", true)}}

# Evaluation

All metrices express the models ability to classify dataset titles from GOVDATA into the taxonomy described [here](https://huggingface.co/datasets/and-effect/mdk_gov_data_titles_clf). For more information see VERLINKUNG MDK Projekt.

## Testing Data, Factors & Metrics

### Testing Data

The evaluation data can be found [here](https://huggingface.co/datasets/and-effect/mdk_gov_data_titles_clf). Since the model is trained on revision 172e61bb1dd20e43903f4c51e5cbec61ec9ae6e6 for evaluation, the evaluation metrics rely on the same revision.

### Metrics

The model performance is tested with fours metrices. Accuracy, Precision, Recall and F1 Score. A lot of classes were not predicted and are thus set to zero for the calculation of precision, recall and f1 score. For these metrices the additional calucations were performed exluding classes with less than two predictions for the level 'Bezeichnung' (see in table results 'Bezeichnung II'. Although intepretation of these results should be interpreted with caution, because they do not represent all classes.

## Results

{{ results | default("[More Information Needed]", true)}}

### Summary

{{ results_summary | default("", true) }}

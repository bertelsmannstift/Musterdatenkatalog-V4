---
# For reference on model card metadata, see the spec: https://github.com/huggingface/hub-docs/blob/main/datasetcard.md?plain=1
# Doc / guide: https://huggingface.co/docs/hub/datasets-cards
{{ card_data }}
---

# Dataset Card for {{ pretty_name | default("Dataset Name", true) }}

## Dataset Description

### Dataset Summary

{{ dataset_summary | default("[More Information Needed]", true)}}

### Languages

The language data is German.

## Dataset Structure

### Data Instances

{{ data_instances_section | default("[More Information Needed]", true)}}

### Data Fields

{{ data_size | default("[More Information Needed]", true)}}

An example of the 'train' looks as follows:

```
{
    'doc_id': 'a063d3b7-4c09-421e-9849-073dc8939e76'
    'title': 'Dienstleistungen Alphabetisch sortiert April 2019'
    'description': 'CSV-Datei mit allen Dienstleistungen der Kreisverwaltung Kleve. Sortiert nach AlphabetStand 01.04.2019'
    'labels_name': 'Sonstiges - Sonstiges'
    'labels': 166
}
```

The data fields are the same among all splits:

- doc_id (uuid): identifier for each document
- title (str): dataset title from GovData
- description (str): description of the dataset
- labels_name (str): annotation with labels from taxonomy
- labels (int): labels indexed from 0 to 250

### Data Splits

{{ dataset_split | default("[More Information Needed]", true)}}

## Dataset Creation

The dataset was created through multiple manual annotation rounds.

### Source Data

The data comes from GovData (GovData)[https://www.govdata.de/], an open data portal of Germany. It aims to provide central access to administrative data from the federal, state and local governments. Their aim is to make data available in one place and thus easier to use. The data available is structured in 13 categories ranging from finance, to international topics, health, education and science and technology. GovData offers a CKAN API to make requests and provides metadata for each data entry.

#### Initial Data Collection and Normalization

Several sources were used for the annotation process. A sample was collected from GovData with actual datasets. For the sample, 50 records were drawn for each group. Additional samples are from (this project)[https://github.com/bertelsmannstift/Musterdatenkatalog] that contain older data from GovData. Some of the datasets from that project already contained an annotation, but since the taxonomy is not the same, the data were re-annotated. A sample was drawn from each source (randomly and by manual selection), resulting in a total of 1258 titles.

### Annotations

#### Annotation process

The data was annotated in four rounds and one additional test round. In each round a percentage of the data was allocated to all annotators to caluculate the inter-annotator agreement using Cohens Kappa.
The following table shows the results of the of the annotations:

|                    | **Cohens Kappa** | **Number of Annotators** | **Number of Documents** |
| ------------------ | :--------------: | ------------------------ | ----------------------- |
| **Test Round**     |       .77        | 6                        | 50                      |
| **Round 1**        |       .41        | 2                        | 120                     |
| **Round 2**        |       .76        | 4                        | 480                     |
| **Round 3**        |       .71        | 3                        | 420                     |
| **Round 4**        |       .87        | 2                        | 416                     |
| **Validation set** |        -         | 1                        | 177                     |

In addition, a validation set was generated by

#### Who are the annotators?

Annotators are all employees of from and-effect.

## Considerations for Using the Data

The dataset for the annotation process was generated by sampling from GovData and data previously collected from GovData. The data on GovData is continuously updated and data can get deleted. Thus, there is no guarantee that data entries included here will also be available on GovData.

<!-- {{ considerations_for_data | default("[More Information Needed]", true)}} -->

### Social Impact of Dataset

{{ social_impact_section | default("[More Information Needed]", true)}}

### Discussion of Biases

The data was mainly sampled at random from the categories available on GovData. Although all categories were sampled there is still some imbalance in the data. For example: entries for the concept 'Raumordnung, Raumplanung und Raumentwicklung - Bebauungsplan' make up the majority class. Although manual selection of data was also used for not all previous concepts data entries was found. However, for 95% of concepts at least one data entry is available.

<!-- {{ discussion_of_biases_section | default("[More Information Needed]", true)}} -->

### Other Known Limitations

We know from training with the data that for some concepts there are too few entries to calculate all evaluation metrics.

<!-- {{ known_limitations_section | default("[More Information Needed]", true)}} -->

## Additional Information

### Dataset Curators

{{ dataset_curators_section | default("[More Information Needed]", true)}}

### Licensing Information

{{ licensing_information_section | default("[More Information Needed]", true)}}

### Citation Information

{{ citation_information_section | default("[More Information Needed]", true)}}

### Contributions

{{ contributions_section | default("[More Information Needed]", true)}}

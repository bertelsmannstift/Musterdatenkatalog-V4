"""
script to convert the taxonomy into skos format
"""
from urllib.parse import urljoin

import pandas as pd
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, SKOS

from src.settings import Settings

settings = Settings(_env_file="paths/.env.dev")


def add_link(input_graph: Graph, identifier: str, link: str, relationship_type: str):
    """adds linking to other database to concept

    Parameters
    ----------
    input_graph : Graph
        graph of the concept to be added to
    identifier : str
        identifier of the concept
    link : str
        link to the other database concept
    relationship_type : str
        skos relationship type
    """
    relation = relationship_type.strip("skos:")
    input_graph.add((name_space[identifier], SKOS[relation], Literal(link, lang="de")))


# importing the excel sheet with all the taxonomy info and the github csv
taxonomy_info = pd.read_excel(settings.TAXONOMY_INFO_V1, na_values="N.A.")

test = pd.read_csv(
    settings.TAXONOMY_INFO_V2, delimiter=",(?! )", quotechar='"', keep_default_na=False
)  # regex: matching ',' without space after it
taxonomy_uri_table = test.applymap(
    lambda x: x.replace('"', "") if (isinstance(x, str)) else x
)


# merging of excel file and Info csv
taxonomy_info["MUSTERDATENSATZ"] = [
    taxonomy_info["THEMA"][index] + " - " + taxonomy_info["BEZEICHNUNG"][index]
    for index, row in taxonomy_info.iterrows()
]

# merging both dataframes
all_info = taxonomy_info.merge(
    taxonomy_uri_table,
    left_on="MUSTERDATENSATZ",
    right_on="MUSTERDATENSATZ",
)  # x = taxonomy_info columns, y = taxonomy_uri_table columns


# checks for after merging
assert all_info["BEZEICHNUNG_x"].equals(all_info["BEZEICHNUNG_y"])
assert all_info["THEMA_x"].equals(all_info["THEMA_y"])
assert all_info["Beschreibung Bezeichnung"].equals(all_info["Beschreibung"])
assert all_info["Topic_x"].equals(all_info["Topic_y"])
assert all_info["Name"].equals(all_info["Label"])

# building URIs
uris = []
for index, row in all_info.iterrows():
    uri_build = row["thema"] + "/" + row["Bezeichnung"]
    if row["Bezeichnung2"]:  # Bezeichnung2 contains theoretical third level
        uri_build = uri_build + "/" + row["Bezeichnung2"]

    uris.append(uri_build)

all_info["URI"] = uris

###########
# Inititalizing graph
taxonomy_graph = Graph()

# namespace
name_space = Namespace(
    "https://musterdatenkatalog.de/def/musterdatensatz/"
)  # parent website for uris

# bind prefixes
taxonomy_graph.bind("Musterdatenkatalog", name_space)
taxonomy_graph.bind("skos", SKOS)
taxonomy_graph.bind("rdf", RDF)

# add skos:conceptScheme
taxonomy_graph.add((name_space["Musterdatenkatalog"], RDF.type, SKOS["ConceptScheme"]))


bezeichnung_counter = 0

# populate graph in two steps: THEMA and BEZEICHNUNG
concept_store = {}
for index, row in all_info.iterrows():
    bezeichnung_counter += 1

    # BEZEICHNUNG
    taxonomy_graph.add((name_space[row["URI"]], RDF.type, SKOS["Concept"]))
    concept_store[row["URI"]] = name_space[row["URI"]]

    # add inScheme
    taxonomy_graph.add(
        (
            name_space[row["URI"]],
            SKOS["inScheme"],
            name_space["Musterdatenkatalog"],
        )
    )

    # preferred label - de
    taxonomy_graph.add(
        (
            name_space[row["URI"]],
            SKOS["prefLabel"],
            Literal(row["BEZEICHNUNG_x"], lang="de"),
        )
    )

    # preferred label - en
    taxonomy_graph.add(
        (
            name_space[row["URI"]],
            SKOS["prefLabel"],
            Literal(row["Name"], lang="en"),
        )
    )
    # definition
    taxonomy_graph.add(
        (
            name_space[row["URI"]],
            SKOS["definition"],
            Literal(row["Beschreibung Bezeichnung"], lang="de"),
        )
    )
    # # adding DND link
    if not pd.isna(row["GND Bezeichnung"]):
        add_link(
            input_graph=taxonomy_graph,
            identifier=row["URI"],
            link=row["GND Bezeichnung"],
            relationship_type=row["GND type Bezeichnung"],
        )
    # adding Wikidata link
    if not pd.isna(row["Wikidata ID Bezeichnung"]):
        add_link(
            input_graph=taxonomy_graph,
            identifier=row["URI"],
            link=row["Wikidata ID Bezeichnung"],
            relationship_type=row["Wikidata type Bezeichnung"],
        )
    # adding Eurovoc link
    if not pd.isna(row["Eurovoc ID Bezeichnung"]):
        add_link(
            input_graph=taxonomy_graph,
            identifier=row["URI"],
            link=row["Eurovoc ID Bezeichnung"],
            relationship_type=row["Eurovoc type Bezeichnung"],
        )
    # adding Schema.org link
    if not pd.isna(row["Schema.org Bezeichnung"]):
        add_link(
            input_graph=taxonomy_graph,
            identifier=row["URI"],
            link=row["Schema.org Bezeichnung"],
            relationship_type=row["Schema type Bezeichnung"],
        )
    # adding editiorial note
    if not pd.isna(row["Anmerkungen"]):
        taxonomy_graph.add(
            (
                name_space[row["URI"]],
                SKOS["editorialNote"],
                Literal(row["Anmerkungen"], lang="de"),
            )
        )

    # THEMA
    if row["thema"] not in concept_store:

        # add concept
        taxonomy_graph.add((name_space[row["thema"]], RDF.type, SKOS["Concept"]))
        # # add inScheme
        taxonomy_graph.add(
            (
                name_space[row["thema"]],
                SKOS["inScheme"],
                name_space["Musterdatenkatalog"],
            )
        )
        # topConceptOf
        taxonomy_graph.add(
            (
                name_space[row["thema"]],
                SKOS["topConceptOf"],
                name_space["Musterdatenkatalog"],
            )
        )
        # adding thema to Musterdatenkatalog
        taxonomy_graph.add(
            (
                name_space["Musterdatenkatalog"],
                SKOS["hasTopConcept"],
                name_space[row["thema"]],
            )
        )

        # add as broader concept
        taxonomy_graph.add(
            (
                name_space[row["URI"]],
                SKOS["broader"],
                name_space[row["thema"]],
            )
        )

        # add narrower concept
        taxonomy_graph.add(
            (
                name_space[row["thema"]],
                SKOS["narrower"],
                name_space[row["URI"]],
            )
        )
        # preferred label - de
        taxonomy_graph.add(
            (
                name_space[row["thema"]],
                SKOS["prefLabel"],
                Literal(row["THEMA_x"], lang="de"),
            )
        )
        # preferred label - en
        taxonomy_graph.add(
            (
                name_space[row["thema"]],
                SKOS["prefLabel"],
                Literal(row["Topic_x"], lang="en"),
            )
        )
        # definition
        taxonomy_graph.add(
            (
                name_space[row["thema"]],
                SKOS["definition"],
                Literal(row["Beschreibung Thema"], lang="de"),
            )
        )
        # # adding DND
        if not pd.isna(row["GND Thema"]):
            add_link(
                input_graph=taxonomy_graph,
                identifier=row["thema"],
                link=row["GND Thema"],
                relationship_type=row["GND type Thema"],
            )
        # adding Wikidata
        if not pd.isna(row["Wikidata ID Thema"]):
            add_link(
                input_graph=taxonomy_graph,
                identifier=row["thema"],
                link=row["Wikidata ID Thema"],
                relationship_type=row["Wikidata type Thema"],
            )
        # adding Eurovoc link
        if not pd.isna(row["Eurovoc ID Thema"]):
            add_link(
                input_graph=taxonomy_graph,
                identifier=row["thema"],
                link=row["Eurovoc ID Thema"],
                relationship_type=row["Eurovoc type Thema"],
            )
        # adding Schema.org link
        if not pd.isna(row["Schema.org Thema"]):
            add_link(
                input_graph=taxonomy_graph,
                identifier=row["thema"],
                link=row["Schema.org Thema"],
                relationship_type=row["Schema type Thema"],
            )
        # adding OGD link as related
        if not pd.isna(row["OGD URI"]):
            add_link(
                input_graph=taxonomy_graph,
                identifier=row["thema"],
                link=row["OGD URI"],
                relationship_type="skos:related",
            )

# testing if all bezeichnungen included
assert bezeichnung_counter == 242

# check and serialize
taxonomy_graph.serialize(
    format="xml",
    encoding="utf-8",
    destination="data/processed/musterdatenkatalog.rdf",
)

# export csv with needed information
necessary_info = all_info[
    [  # other table content
        "MUSTERDATENSATZ",
        "THEMA_x",
        "BEZEICHNUNG_x",
        "URI",
        # Thema info
        "Topic_x",
        "Beschreibung Thema",
        "OGD URI",
        "GND Thema",
        "GND type Thema",
        "Wikidata ID Thema",
        "Wikidata type Thema",
        "Eurovoc ID Thema",
        "Eurovoc type Thema",
        "Schema.org Thema",
        "Schema type Thema",
        # Bezeichnung info
        "Name",
        "Beschreibung Bezeichnung",
        "GND Bezeichnung",
        "GND type Bezeichnung",
        "Wikidata ID Bezeichnung",
        "Wikidata type Bezeichnung",
        "Eurovoc ID Bezeichnung",
        "Eurovoc type Bezeichnung",
        "Schema.org Bezeichnung",
        "Schema type Bezeichnung",
        # editiorial note
        "Anmerkungen",
    ]
]

# adding URI link
necessary_info["URI"] = necessary_info["URI"].apply(
    lambda x: urljoin("https://musterdatenkatalog.de/def/musterdatensatz/", x)
)

necessary_info = necessary_info.rename(
    columns={"THEMA_x": "THEMA", "Topic_x": "Topic", "BEZEICHNUNG_x": "BEZEICHNUNG"}
)

necessary_info.to_csv("data/processed/MDK_taxonomy_info.csv", index=False)

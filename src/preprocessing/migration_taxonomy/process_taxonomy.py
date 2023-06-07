"""
script processed the old taxonomy and the old data.
It makes the changes discussed and serves as a tracking
file for all the changes
"""
import pandas as pd

from src.settings import Settings
from src.utils.data import load_json, load_txt, save_json
from src.utils.preprocessing_functions import (
    data_delete_concept,
    data_move_concept,
    data_rename_concept,
    generate_excel_log,
    taxonomy_add_concept,
    taxonomy_delete_concept,
    taxonomy_rename_concept,
    taxonomy_rename_or_delete_concept,
)

# Import of taxonomy and dataset
settings = Settings(_env_file="paths/.env.dev")
taxonomy = load_json(path=str(settings.TAXONOMY_PROCESSED_V1))
data = pd.read_csv(settings.BASELINE_MDK_TRAINING_DATA_PROCESSED_V1)
singular_bezeichnung = load_txt(str(settings.SINGULAR_NAMES))
plural_bezeichnung = load_txt(str(settings.PLURAL_NAMES))


######
# Sonstiges
######
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Sonstiges", new_label_name="Sonstiges"
)

######
# TYPOS
######

taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Personal",
    new_group_name="Personal",
    old_label_name="Stellenauschreibungen",
    new_label_name="Stellenausschreibungen",
    node_type="all",
)

data = data_rename_concept(
    data,
    old_group_name=None,
    new_group_name=None,
    old_label_name="Stellenauschreibungen",
    new_label_name="Stellenausschreibungen",
    node_type="label",
)

# deleting typos in taxonomy
typos_bezeichnungen = ["Messtellen", "Kindertagestätten"]
for typo in typos_bezeichnungen:
    taxonomy = taxonomy_delete_concept(
        taxonomy=taxonomy, old_group_name=None, old_label_name=typo, node_type="label"
    )
taxonomy = taxonomy_delete_concept(
    taxonomy=taxonomy,
    old_group_name="Infrastrukur",
    old_label_name=None,
    node_type="group",
)

# renaming typos in data
old = ["Messtellen", "Kindertagestätten"]
new = ["Messstellen", "Kindertagesstätten"]
for a, b in zip(old, new):
    data = data_rename_concept(
        data=data,
        old_group_name=None,
        new_group_name=None,
        old_label_name=a,
        new_label_name=b,
        node_type="label",
    )
old = ["Infrastrukur"]
new = ["Infrastruktur"]
for a, b in zip(old, new):
    data = data_rename_concept(
        data=data,
        old_group_name=a,
        new_group_name=b,
        old_label_name=None,
        new_label_name=None,
        node_type="group",
    )

######
# DUPLICATES
######

# deleting duplicates in taxonomy
duplicates_bezeichnungen = [
    "Wahlergebnis Bundestagswahlen",
    "Wahlergebnis Landtagswahlen",
    "Einwohnerzahlen",
]

for duplicate in duplicates_bezeichnungen:
    taxonomy = taxonomy_delete_concept(
        taxonomy=taxonomy,
        old_group_name=None,
        old_label_name=duplicate,
        node_type="label",
    )

# renaming duplicates in data
old = [
    "Wahlergebnis Bundestagswahlen",
    "Wahlergebnis Landtagswahlen",
    "Einwohnerzahlen",
]
new = ["Wahlergebnis Bundestagswahl", "Wahlergebnis Landtagswahl", "Einwohnerzahl"]
for a, b in zip(old, new):
    data = data_rename_concept(
        data=data,
        old_group_name=None,
        new_group_name=None,
        old_label_name=a,
        new_label_name=b,
        node_type="label",
    )


#####
# DELETING ONLY FIRST LEVEL groups
#####

taxonomy = taxonomy_delete_concept(
    taxonomy=taxonomy, old_group_name="Wohnen", old_label_name="Wohnen", node_type="all"
)
data = data_delete_concept(
    data=data, old_group_name="Wohnen", old_label_name="Wohnen", node_type="all"
)


######
# taxonomy cleaning
#####
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Sport", old_label_name="und Spielstätten", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Sport", old_label_name="und Spielstätten", node_type="all"
)


######
# RENAMING PLURAL TO SINGULAR BEZEICHNUNGEN
######


if len(plural_bezeichnung) != len(singular_bezeichnung):
    raise ValueError("plural and singular uneven")

for a, b in zip(plural_bezeichnung, singular_bezeichnung):
    taxonomy = taxonomy_rename_concept(
        taxonomy=taxonomy,
        old_group_name=None,
        new_group_name=None,
        old_label_name=a,
        new_label_name=b,
        node_type="label",
    )
for a, b in zip(plural_bezeichnung, singular_bezeichnung):
    data = data_rename_concept(
        data=data,
        old_group_name=None,
        new_group_name=None,
        old_label_name=a,
        new_label_name=b,
        node_type="label",
    )


########
# SICHERHEIT
# Remodeling for the category "Sicherheit"
#######

# remove Karneval
taxonomy = taxonomy_delete_concept(
    taxonomy=taxonomy, old_group_name=None, old_label_name="Karneval", node_type="label"
)
data = data_delete_concept(
    data, old_group_name=None, old_label_name="Karneval", node_type="label"
)
# remove Silvester
taxonomy = taxonomy_delete_concept(
    taxonomy=taxonomy,
    old_group_name=None,
    old_label_name="Silvester",
    node_type="label",
)
data = data_delete_concept(
    data, old_group_name=None, old_label_name="Silvester", node_type="label"
)

# add new entry Rettungshilfe - Notinsel
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Sicherheit", new_label_name="Rettungshilfe - Notinsel"
)
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name=None, old_label_name="Notinsel", node_type="label"
)
# transfer Sicherheit - Notinsel data
data = data_rename_concept(
    data,
    old_group_name=None,
    new_group_name=None,
    old_label_name="Notinsel",
    new_label_name="Rettungshilfe - Notinsel",
    node_type="label",
)

# add concept Feuerwehr - Standort
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Sicherheit", new_label_name="Feuerwehr - Standort"
)
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Feuerwehr", old_label_name="Einrichtung", node_type="all"
)

# move concept
data = data_move_concept(
    data,
    old_group_name="Feuerwehr",
    new_group_name="Sicherheit",
    old_label_name="Einrichtung",
    new_label_name="Feuerwehr - Standort",
)

# add concept Feuerwehreinsatz
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Sicherheit", new_label_name="Feuerwehr - Feuerwehreinsatz"
)
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Feuerwehr", old_label_name="Einsatz", node_type="all"
)

data = data_move_concept(
    data,
    old_group_name="Feuerwehr",
    new_group_name="Sicherheit",
    old_label_name="Einsatz",
    new_label_name="Feuerwehr - Feuerwehreinsatz",
)
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Sicherheit", new_label_name="Feuerwehr - Personal"
)
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Feuerwehr", old_label_name="Personal", node_type="all"
)
# deleting Kennzahlen
data = data_delete_concept(
    data=data, old_group_name="Feuerwehr", old_label_name="Kennzahl", node_type="all"
)
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Feuerwehr", old_label_name="Kennzahl", node_type="all"
)

# Infrastruktur - Polizei zu Sicherheit - Polizei
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Sicherheit", new_label_name="Polizei"
)
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Externe Infrastruktur",
    old_label_name="Polizei",
    node_type="all",
)
# move concepts
data = data_move_concept(
    data,
    old_group_name="Externe Infrastruktur",
    new_group_name="Sicherheit",
    old_label_name="Polizei",
    new_label_name="Polizei",
)

# Infrastruktur - Beleuchtung zu Sicherheit - Beleuchtung
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Sicherheit", new_label_name="Beleuchtung"
)
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Infrastruktur",
    old_label_name="Beleuchtung",
    node_type="all",
)
# move concepts
data = data_move_concept(
    data,
    old_group_name="Infrastruktur",
    new_group_name="Sicherheit",
    old_label_name="Beleuchtung",
    new_label_name="Beleuchtung",
)
# Rettungsdienst - Defibrillator zu Gesundheit - Rettungsdienst - Defibrillator
taxonomy = taxonomy_add_concept(
    taxonomy,
    new_group_name="Gesundheit",
    new_label_name="Rettungsdienst - Defibrillator",
)
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Rettungsdienst",
    old_label_name="Defibrillator",
    node_type="all",
)
# move concepts
data = data_move_concept(
    data,
    old_group_name="Rettungsdienst",
    new_group_name="Gesundheit",
    old_label_name="Defibrillator",
    new_label_name="Rettungsdienst - Defibrillator",
)

# Rettungsdienst - Einsatz zu Gesundheit - Rettungsdienst - Rettungsdiensteinsatz
taxonomy = taxonomy_add_concept(
    taxonomy,
    new_group_name="Gesundheit",
    new_label_name="Rettungsdienst - Rettungsdiensteinsatz",
)
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Rettungsdienst", old_label_name="Einsatz", node_type="all"
)
# move concepts
data = data_move_concept(
    data,
    old_group_name="Rettungsdienst",
    new_group_name="Gesundheit",
    old_label_name="Einsatz",
    new_label_name="Rettungsdienst - Rettungsdiensteinsatz",
)

# delete Rettungsdienst - Reanimation
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Rettungsdienst",
    old_label_name="Reanimation",
    node_type="all",
)
data = data_delete_concept(
    data=data,
    old_group_name="Rettungsdienst",
    old_label_name="Reanimation",
    node_type="all",
)


# Rettungsdienst - Waldrettungspunkt - Rettungshilfe - Waldrettungspunkt
taxonomy = taxonomy_add_concept(
    taxonomy,
    new_group_name="Sicherheit",
    new_label_name="Rettungshilfe - Waldrettungspunkt",
)
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Rettungsdienst",
    old_label_name="Waldrettungspunkt",
    node_type="all",
)
# move concepts
data = data_move_concept(
    data,
    old_group_name="Rettungsdienst",
    new_group_name="Sicherheit",
    old_label_name="Waldrettungspunkt",
    new_label_name="Rettungshilfe - Waldrettungspunkt",
)

# Zivil und Katastrophenschutuz - Kampfmittelfunde zu
# Sicherheit - Zivil und Katastrophenschutz - Kampmittelfunde
taxonomy = taxonomy_add_concept(
    taxonomy,
    new_group_name="Sicherheit",
    new_label_name="Zivil und Katastrophenschutz - Kampfmittelfund",
)
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Zivil und Katastrophenschutz",
    old_label_name="Kampfmittelfund",
    node_type="all",
)
# move concepts
data = data_move_concept(
    data,
    old_group_name="Zivil und Katastrophenschutz",
    new_group_name="Sicherheit",
    old_label_name="Kampfmittelfund",
    new_label_name="Zivil und Katastrophenschutz - Kampfmittelfund",
)
# Zivil und Katastrophenschutuz - Sirene zu Sicherheit - Zivil und Katastrophenschutz - Sirene
taxonomy = taxonomy_add_concept(
    taxonomy,
    new_group_name="Sicherheit",
    new_label_name="Zivil und Katastrophenschutz - Sirene",
)
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Zivil und Katastrophenschutz",
    old_label_name="Sirene",
    node_type="all",
)
# move concepts
data = data_move_concept(
    data,
    old_group_name="Zivil und Katastrophenschutz",
    new_group_name="Sicherheit",
    old_label_name="Sirene",
    new_label_name="Zivil und Katastrophenschutz - Sirene",
)
# Freizeit - Norfallnummer zu Sicherheit - Rettungshilfe - Notfallnummer
taxonomy = taxonomy_add_concept(
    taxonomy,
    new_group_name="Sicherheit",
    new_label_name="Rettungshilfe - Notfallnummer",
)
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Freizeit",
    old_label_name="Notfallnummer",
    node_type="all",
)
# move concepts
data = data_move_concept(
    data,
    old_group_name="Zivil und Katastrophenschutz",
    new_group_name="Sicherheit",
    old_label_name="Notfallnummer",
    new_label_name="Rettungshilfe - Notfallnummer",
)

# add Sicherheit - Anlaufstelle
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Sicherheit", new_label_name="Rettungshilfe - Anlaufstelle"
)


########
# ENERGIE
#######

# renaming group Energiewirtschaft
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Energiewirtschaft",
    new_group_name="Energie",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)
data = data_rename_concept(
    data,
    old_group_name="Energiewirtschaft",
    new_group_name="Energie",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)
# renaming bezeichnung Heizung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name=None,
    new_group_name=None,
    old_label_name="Heizung",
    new_label_name="Wärmeversorgung",
    node_type="label",
)
data = data_rename_concept(
    data,
    old_group_name=None,
    new_group_name=None,
    old_label_name="Heizung",
    new_label_name="Wärmeversorgung",
    node_type="label",
)
# renaming bezeichnung Heizung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name=None,
    new_group_name=None,
    old_label_name="Wasser",
    new_label_name="Wasserversorgung",
    node_type="label",
)
data = data_rename_concept(
    data,
    old_group_name=None,
    new_group_name=None,
    old_label_name="Wasser",
    new_label_name="Wasserversorgung",
    node_type="label",
)
# renaming bezeichnung Strom
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Energie",
    new_group_name="Energie",
    old_label_name="Strom",
    new_label_name="Stromversorgung",
    node_type="label",
)
data = data_rename_concept(
    data,
    old_group_name="Energie",
    new_group_name="Energie",
    old_label_name="Strom",
    new_label_name="Stromversorgung",
    node_type="label",
)


# Windenergie
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Energie", new_label_name="Windenergie"
)

########
# FREIZEIT
#######
# renaming bezeichnung Bad
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Freizeit",
    new_group_name="Freizeit",
    old_label_name="Bad",
    new_label_name="Bad und Freibad",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Freizeit",
    new_group_name="Freizeit",
    old_label_name="Bad",
    new_label_name="Bad und Freibad",
)
# merging in Schwimmäder
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Schwimmbäder",
    new_group_name="Freizeit",
    old_label_name="Besucher",
    new_label_name="Bad und Freibad",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Schwimmbäder",
    new_group_name="Freizeit",
    old_label_name="Besucher",
    new_label_name="Bad und Freibad",
)
# moving Spielplatz und Spielstätte - Freibad into Freizeit - Bad und Freibad
taxonomy = taxonomy_delete_concept(
    taxonomy=taxonomy,
    old_group_name="Spielplatz und Spielstätte",
    old_label_name="Freibad",
    node_type="all",
)
data = data_move_concept(
    data=data,
    old_group_name="Spielplatz und Spielstätte",
    new_group_name="Freizeit",
    old_label_name="Freibad",
    new_label_name="Bad und Freibad",
)
# removing Spielplätze und Spielstätte (moving Einrichtungen, deleting Belegung)
taxonomy = taxonomy_delete_concept(
    taxonomy=taxonomy,
    old_group_name="Spielplatz und Spielstätte",
    old_label_name="Belegung",
    node_type="all",
)
taxonomy = taxonomy_delete_concept(
    taxonomy=taxonomy,
    old_group_name="Spielplatz und Spielstätte",
    old_label_name="Einrichtung",
    node_type="all",
)
taxonomy_add_concept(
    taxonomy, new_group_name="Freizeit", new_label_name="Spielplatz und Spielstätte "
)
data = data_move_concept(
    data=data,
    old_group_name="Spielplatz und Spielstätte",
    new_group_name="Freizeit",
    old_label_name="Einrichtung",
    new_label_name="Spielplatz und Spielstätte ",
)


######
# all to do with Sport/Spiel / cleaning rest up
######

# Sport und Spielplätze -> Freizeit - Spielplatz und Spielstätte
# Einrichtung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Sport und Spielplätze",
    new_group_name="Freizeit",
    old_label_name="Einrichtung",
    new_label_name="Spielplatz und Spielstätte ",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Sport und Spielplätze",
    new_group_name="Freizeit",
    old_label_name="Einrichtung",
    new_label_name="Spielplatz und Spielstätte ",
)

# Sport und Spielstätten
# Einrichtung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Sport und Spielstätten",
    new_group_name="Freizeit",
    old_label_name="Einrichtung",
    new_label_name="Spielplatz und Spielstätte ",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Sport und Spielstätten",
    new_group_name="Freizeit",
    old_label_name="Einrichtung",
    new_label_name="Spielplatz und Spielstätte ",
)

# Belegung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Sport und Spielstätten",
    new_group_name="Freizeit",
    old_label_name="Belegung",
    new_label_name="Spielplatz und Spielstätte ",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Sport und Spielstätten",
    new_group_name="Freizeit",
    old_label_name="Belegung",
    new_label_name="Spielplatz und Spielstätte ",
)
# Freibad
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Sport und Spielstätten",
    new_group_name="Freizeit",
    old_label_name="Freibad",
    new_label_name="Bad und Freibad",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Sport und Spielstätten",
    new_group_name="Freizeit",
    old_label_name="Freibad",
    new_label_name="Bad und Freibad",
)


# adding two more for Freizeit
taxonomy_add_concept(
    taxonomy, new_group_name="Freizeit", new_label_name="Jugendeinrichtung"
)
taxonomy_add_concept(taxonomy, new_group_name="Freizeit", new_label_name="Verein")

taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Jugend",
    new_group_name="Freizeit",
    old_label_name="Einrichtung",
    new_label_name="Jugendeinrichtung",
    node_type="all",
)

data = data_move_concept(
    data=data,
    old_group_name="Jugend",
    new_group_name="Freizeit",
    old_label_name="Einrichtung",
    new_label_name="Jugendeinrichtung",
)

# delete Einrichtung
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Freizeit", old_label_name="Einrichtung", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Freizeit", old_label_name="Einrichtung", node_type="all"
)


########
# JUSTIZ
#######
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Justiz",
    new_group_name="Justiz",
    old_label_name="Einrichtung",
    new_label_name="Justizeinrichtung",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Justiz",
    new_group_name="Justiz",
    old_label_name="Einrichtung",
    new_label_name="Justizeinrichtung",
)

########
# GESCHICHTE
#######
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Geschichte", new_label_name="Standort mit Geschichte"
)
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Geschichte", new_label_name="Quelle - Historische Karte"
)

# renaming of Archivbestand
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Geschichte",
    new_group_name="Geschichte",
    old_label_name="Archivbestand",
    new_label_name="Quelle - Archivbestand",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Geschichte",
    new_group_name="Geschichte",
    old_label_name="Archivbestand",
    new_label_name="Quelle - Archivbestand",
)

# merging in Stadtarchiv - Bestand
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Stadtarchiv",
    new_group_name="Geschichte",
    old_label_name="Bestand",
    new_label_name="Quelle - Archivbestand",
    node_type="all",
)


data = data_move_concept(
    data,
    old_group_name="Stadtarchiv",
    new_group_name="Geschichte",
    old_label_name="Bestand",
    new_label_name="Quelle - Archivbestand",
)

# renaming of historischr Luftaufnahmen
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Geschichte",
    new_group_name="Geschichte",
    old_label_name="Historische Luftaufnahme",
    new_label_name="Quelle - Historische Luftaufnahme",
    node_type="all",
)


data = data_move_concept(
    data,
    old_group_name="Geschichte",
    new_group_name="Geschichte",
    old_label_name="Historische Luftaufnahme",
    new_label_name="Quelle - Historische Luftaufnahme",
)

# renaming of Entschädigung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Geschichte",
    new_group_name="Geschichte",
    old_label_name="Entschädigung",
    new_label_name="Quelle - Entschädigung",
    node_type="all",
)


data = data_move_concept(
    data,
    old_group_name="Geschichte",
    new_group_name="Geschichte",
    old_label_name="Entschädigung",
    new_label_name="Quelle - Entschädigung",
)
# renaming of Personalverzeichnis historisch
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Geschichte",
    new_group_name="Geschichte",
    old_label_name="Personalverzeichnis historisch",
    new_label_name="Quelle - Personalverzeichnis",
    node_type="all",
)


data = data_move_concept(
    data,
    old_group_name="Geschichte",
    new_group_name="Geschichte",
    old_label_name="Personalverzeichnis historisch",
    new_label_name="Quelle - Personalverzeichnis",
)

# delete Geschichte - Information
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Geschichte", old_label_name="Information", node_type="all"
)
data = data_delete_concept(
    data, old_group_name="Geschichte", old_label_name="Information", node_type="all"
)

#####
# Öffentlichkeitsarbeit
#####

# deleting Amtsblatt
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Öffentlichkeitsarbeit",
    old_label_name="Amtsblatt",
    node_type="all",
)
data = data_delete_concept(
    data,
    old_group_name="Öffentlichkeitsarbeit",
    old_label_name="Amtsblatt",
    node_type="all",
)
# deleting Ehrenbürger
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Öffentlichkeitsarbeit",
    old_label_name="Ehrenbürger",
    node_type="all",
)
data = data_delete_concept(
    data,
    old_group_name="Öffentlichkeitsarbeit",
    old_label_name="Ehrenbürger",
    node_type="all",
)
# deleting Fotos
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Öffentlichkeitsarbeit",
    old_label_name="Foto",
    node_type="all",
)
data = data_delete_concept(
    data,
    old_group_name="Öffentlichkeitsarbeit",
    old_label_name="Foto",
    node_type="all",
)
# merging Information und Pressemitteilung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Öffentlichkeitsarbeit",
    new_group_name="Öffentlichkeitsarbeit",
    old_label_name="Information",
    new_label_name="Pressemitteilung und Veröffentlichung",
    node_type="all",
)
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Öffentlichkeitsarbeit",
    old_label_name="Pressemitteilung",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Öffentlichkeitsarbeit",
    new_group_name="Öffentlichkeitsarbeit",
    old_label_name="Information",
    new_label_name="Pressemitteilung und Veröffentlichung",
)
data = data_move_concept(
    data,
    old_group_name="Öffentlichkeitsarbeit",
    new_group_name="Öffentlichkeitsarbeit",
    old_label_name="Pressemitteilung",
    new_label_name="Pressemitteilung und Veröffentlichung",
)

# cleaning Stadtmarketing
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Stadtmarketing",
    old_label_name="Werbeträger",
    node_type="all",
)


data = data_delete_concept(
    data, old_group_name="Stadtmarketing", old_label_name="Werbeträger", node_type="all"
)

# merging stadtmarketing into Öffentlichkeitsarbeit
# Information
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Stadtmarketing",
    new_group_name="Öffentlichkeitsarbeit",
    old_label_name="Information",
    new_label_name="Stadtmarketing",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Stadtmarketing",
    new_group_name="Öffentlichkeitsarbeit",
    old_label_name="Information",
    new_label_name="Stadtmarketing",
)
# Städteranking
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Stadtmarketing",
    new_group_name="Öffentlichkeitsarbeit",
    old_label_name="Städteranking",
    new_label_name="Stadtmarketing",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Stadtmarketing",
    new_group_name="Öffentlichkeitsarbeit",
    old_label_name="Städteranking",
    new_label_name="Stadtmarketing",
)
# Standortentwicklung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Stadtmarketing",
    new_group_name="Öffentlichkeitsarbeit",
    old_label_name="Standortentwicklung",
    new_label_name="Stadtmarketing",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Stadtmarketing",
    new_group_name="Öffentlichkeitsarbeit",
    old_label_name="Standortentwicklung",
    new_label_name="Stadtmarketing",
)
# Zahlen und Fakten
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Stadtmarketing",
    new_group_name="Öffentlichkeitsarbeit",
    old_label_name="Zahlen und Fakten",
    new_label_name="Stadtmarketing",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Stadtmarketing",
    new_group_name="Öffentlichkeitsarbeit",
    old_label_name="Zahlen und Fakten",
    new_label_name="Stadtmarketing",
)
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Stadtmarketing", old_label_name=None, node_type="group"
)


# merging parts of Öffentliche Wirtschaft into Öffentlichekeitsarbeit
# Pressemitteilung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Öffentliche Wirtschaft",
    new_group_name="Öffentlichkeitsarbeit",
    old_label_name="Pressemitteilung",
    new_label_name="Pressemitteilung und Veröffentlichung",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Öffentliche Wirtschaft",
    new_group_name="Öffentlichkeitsarbeit",
    old_label_name="Pressemitteilung",
    new_label_name="Pressemitteilung und Veröffentlichung",
)
# Information
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Öffentliche Wirtschaft",
    new_group_name="Öffentlichkeitsarbeit",
    old_label_name="Information",
    new_label_name="Pressemitteilung und Veröffentlichung",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Öffentliche Wirtschaft",
    new_group_name="Öffentlichkeitsarbeit",
    old_label_name="Information",
    new_label_name="Pressemitteilung und Veröffentlichung",
)
# delete not merged labels

# Amtsblatt
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Öffentliche Wirtschaft",
    old_label_name="Amtsblatt",
    node_type="all",
)

data = data_delete_concept(
    data,
    old_group_name="Öffentlichkeitsarbeit",
    old_label_name="Amtsblatt",
    node_type="all",
)
# Ehrenbürger
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Öffentliche Wirtschaft",
    old_label_name="Ehrenbürger",
    node_type="all",
)

data = data_delete_concept(
    data,
    old_group_name="Öffentlichkeitsarbeit",
    old_label_name="Ehenbürger",
    node_type="all",
)
# Foto
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Öffentliche Wirtschaft",
    old_label_name="Foto",
    node_type="all",
)

data = data_delete_concept(
    data, old_group_name="Öffentlichkeitsarbeit", old_label_name="Foto", node_type="all"
)


######
# Open Data / Digitalisierung
######

# creating new levels
taxonomy = taxonomy_add_concept(
    taxonomy,
    new_group_name="Digitalisierung",
    new_label_name="Open Data - Zugriffszahl",
)
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Digitalisierung", new_label_name="Open Data - Planung"
)
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Digitalisierung", new_label_name="WLAN und Mobilfunk"
)

# removing typo from Taxonomy
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Website",
    new_group_name="Digitalisierung",
    old_label_name="Zugriff",
    new_label_name="Webseite",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Website",
    new_group_name="Digitalisierung",
    old_label_name="Zugriff",
    new_label_name="Webseite",
)

# merging Open Data into Digitalisierung
data = data_move_concept(
    data,
    old_group_name="Open Data",
    new_group_name="Digitalisierung",
    old_label_name="Wunschliste",
    new_label_name="Open Data - Planung",
)
data = data_move_concept(
    data,
    old_group_name="Open Data",
    new_group_name="Digitalisierung",
    old_label_name="Zugriff",
    new_label_name="Open Data - Zugriffszahl",
)
# Webseite
data = data_move_concept(
    data,
    old_group_name="Webseite",
    new_group_name="Digitalisierung",
    old_label_name="Zugriff",
    new_label_name="Webseite",
)
data = data_move_concept(
    data,
    old_group_name="Open Data",
    new_group_name="Digitalisierung",
    old_label_name="Zugriff",
    new_label_name="Webseite",
)
data = data_delete_concept(
    data, old_group_name="Open Data", old_label_name="Information", node_type="all"
)

taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Open Data", old_label_name=None, node_type="group"
)

######
# Finanzen / old: Haushalt
######

# renaming of categories kept in Finanzen - Haushalt
# Außerplanmäßige Aufwendung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Außerplanmäßige Aufwendung",
    new_label_name="Haushalt - Außerplanmäßige Aufwendung",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Außerplanmäßige Aufwendung",
    new_label_name="Haushalt - Außerplanmäßige Aufwendung",
)
# Controlling
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Controlling",
    new_label_name="Haushalt - Controlling",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Controlling",
    new_label_name="Haushalt - Controlling",
)

# Produktbereichssumme
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Produktbereichssumme",
    new_label_name="Haushalt - Produktbereichssumme",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Produktbereichssumme",
    new_label_name="Haushalt - Produktbereichssumme",
)
# Jahresabschluss
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Jahresabschluss",
    new_label_name="Haushalt - Jahresabschluss",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Jahresabschluss",
    new_label_name="Haushalt - Jahresabschluss",
)
# Satzung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Satzung",
    new_label_name="Haushalt - Satzung",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Satzung",
    new_label_name="Haushalt - Satzung",
)
# Produktplan
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Produktplan",
    new_label_name="Haushalt - Produktplan",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Produktplan",
    new_label_name="Haushalt - Produktplan",
)
# Sponsoring
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Sponsoring",
    new_label_name="Haushalt - Sponsoring",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Sponsoring",
    new_label_name="Haushalt - Sponsoring",
)
# Merge Zuwendung und Förderung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Zuwendung Politische Gremien",
    new_label_name="Haushalt - Zuwendung und Förderung",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Zuwendung Politische Gremien",
    new_label_name="Haushalt - Sponsoring",
)
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Förderung",
    new_label_name="Haushalt - Zuwendung und Förderung",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Förderung",
    new_label_name="Haushalt - Sponsoring",
)
# Merge - Plan
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Ergebnisplan",
    new_label_name="Haushalt - Plan",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Ergebnisplan",
    new_label_name="Haushalt - Plan",
)
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Finanzplan",
    new_label_name="Haushalt - Plan",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Finanzplan",
    new_label_name="Haushalt - Plan",
)
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Haushaltsplan",
    new_label_name="Haushalt - Plan",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Haushalt",
    new_group_name="Finanzen",
    old_label_name="Haushaltsplan",
    new_label_name="Haushalt - Plan",
)
# Delete Rest
# Eckdaten
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Haushalt", old_label_name="Eckdaten", node_type="all"
)
data = data_delete_concept(
    data, old_group_name="Haushalt", old_label_name="Eckdaten", node_type="all"
)
# Einzeldarstellung
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Haushalt",
    old_label_name="Einzeldarstellung",
    node_type="all",
)
data = data_delete_concept(
    data,
    old_group_name="Haushalt",
    old_label_name="Einzeldarstellung",
    node_type="all",
)
# Haushaltskonsolidierung
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Haushalt",
    old_label_name="Haushaltskonsolidierung",
    node_type="all",
)
data = data_delete_concept(
    data,
    old_group_name="Haushalt",
    old_label_name="Haushaltskonsolidierung",
    node_type="all",
)
# Metadaten
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Haushalt", old_label_name="Metadaten", node_type="all"
)
data = data_delete_concept(
    data, old_group_name="Haushalt", old_label_name="Metadaten", node_type="all"
)
# Produktgruppe
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Haushalt", old_label_name="Produktgruppe", node_type="all"
)
data = data_delete_concept(
    data, old_group_name="Haushalt", old_label_name="Produktgruppe", node_type="all"
)
# Sicherungskonzept
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Haushalt",
    old_label_name="Sicherungskonzept",
    node_type="all",
)
data = data_delete_concept(
    data,
    old_group_name="Haushalt",
    old_label_name="Sicherungskonzept",
    node_type="all",
)
# Merge Steuern und Abgaben into Haushalt
# Hundesteuer
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Steuern und Abgaben",
    new_group_name="Finanzen",
    old_label_name="Hundesteuer",
    new_label_name="Steuern und Abgaben",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Steuern und Abgaben",
    new_group_name="Finanzen",
    old_label_name="Hundesteuer",
    new_label_name="Steuern und Abgaben",
)
# Nettoeinnahme
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Steuern und Abgaben",
    new_group_name="Finanzen",
    old_label_name="Nettoeinnahme",
    new_label_name="Steuern und Abgaben",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Steuern und Abgaben",
    new_group_name="Finanzen",
    old_label_name="Nettoeinnahme",
    new_label_name="Steuern und Abgaben",
)

######
# Klima und Umweltschutz
######

# Umweltzone
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Umweltschutz",
    new_group_name="Klima und Umweltschutz",
    old_label_name="Umweltzone",
    new_label_name="Umweltzone",
    node_type="all",
)
data = data_rename_concept(
    data,
    old_group_name="Umweltschutz",
    new_group_name="Klima und Umweltschutz",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)
# Klimabilanz
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Umweltschutz",
    new_group_name="Klima und Umweltschutz",
    old_label_name="Klimabilanz",
    new_label_name="Bericht und Analyse - Klimabilanz",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Umweltschutz",
    new_group_name="Klima und Umweltschutz",
    old_label_name="Klimabilanz",
    new_label_name="Bericht und Analyse - Klimabilanz",
)
# Grundwasser
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Umweltschutz",
    new_group_name="Klima und Umweltschutz",
    old_label_name="Grundwasser",
    new_label_name="Bericht und Analyse - Wasser",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Umweltschutz",
    new_group_name="Klima und Umweltschutz",
    old_label_name="Grundwasser",
    new_label_name="Bericht und Analyse - Wasser",
)
# Trinkwasser
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Umweltschutz",
    new_group_name="Klima und Umweltschutz",
    old_label_name="Trinkwasser",
    new_label_name="Bericht und Analyse - Wasser",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Umweltschutz",
    new_group_name="Klima und Umweltschutz",
    old_label_name="Trinkwasser",
    new_label_name="Bericht und Analyse - Wasser",
)
# Messstelle
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Umweltschutz",
    new_group_name="Klima und Umweltschutz",
    old_label_name="Messstelle",
    new_label_name="Bericht und Analyse - Verkehrsmessung",
    node_type="all",
)
data = data_delete_concept(
    data, old_group_name="Umweltschutz", old_label_name="Messstelle", node_type="all"
)
# Messstelle
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Umweltschutz",
    new_group_name="Klima und Umweltschutz",
    old_label_name="Nachhaltigkeit",
    new_label_name="Bericht und Analyse - Luft und Emission",
    node_type="all",
)
data = data_delete_concept(
    data,
    old_group_name="Umweltschutz",
    old_label_name="Nachhaltigkeit",
    node_type="all",
)

# Radioaktivitätsmessung
taxonomy = taxonomy_add_concept(
    taxonomy,
    new_group_name="Klima und Umweltschutz",
    new_label_name="Radioaktivitätsmessung",
)

######
# Raumordnung - transform to Raumordnung, Raumplanung und Raumentwicklung
######

# merge multiple into Raumordnung - Raumgliederung und Gebietseinteilung
# Adresse
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Raumordnung",
    new_group_name="Raumordnung",
    old_label_name="Adresse",
    new_label_name="Raumgliederung - Adresse",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Raumordnung",
    new_group_name="Raumordnung",
    old_label_name="Adresse",
    new_label_name="Raumgliederung - Adresse",
)
# Hausnummer
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Raumordnung",
    new_group_name="Raumordnung",
    old_label_name="Hausnummer",
    new_label_name="Raumgliederung - Hausnummer",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Raumordnung",
    new_group_name="Raumordnung",
    old_label_name="Hausnummer",
    new_label_name="Raumgliederung - Hausnummer",
)
# Block
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Raumordnung",
    new_group_name="Raumordnung",
    old_label_name="Block",
    new_label_name="Raumgliederung - Block",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Raumordnung",
    new_group_name="Raumordnung",
    old_label_name="Block",
    new_label_name="Raumgliederung - Block",
)
# Postleitzahlengebiet
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Raumordnung",
    new_group_name="Raumordnung",
    old_label_name="Postleitzahlengebiet",
    new_label_name="Raumgliederung - Postleitzahlengebiet",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Raumordnung",
    new_group_name="Raumordnung",
    old_label_name="Postleitzahlengebiet",
    new_label_name="Raumgliederung - Postleitzahlengebiet",
)
# Stadtgebiet
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Raumordnung",
    new_group_name="Raumordnung",
    old_label_name="Stadtgebiet",
    new_label_name="Raumgliederung - Stadtgebiet",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Raumordnung",
    new_group_name="Raumordnung",
    old_label_name="Stadtgebiet",
    new_label_name="Raumgliederung - Stadtgebiet",
)
# Ortsteil
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Raumordnung",
    new_group_name="Raumordnung",
    old_label_name="Ortsteil",
    new_label_name="Raumgliederung - Ortsteil",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Raumordnung",
    new_group_name="Raumordnung",
    old_label_name="Ortsteil",
    new_label_name="Raumgliederung - Ortsteil",
)
# delete Baublockgrenze
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Raumordnung",
    old_label_name="Baublockgrenze",
    node_type="all",
)
data = data_delete_concept(
    data,
    old_group_name="Raumordnung",
    old_label_name="Baublockgrenze",
    node_type="all",
)

# Liegenschaftenkataster
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Raumordnung",
    new_group_name="Raumordnung",
    old_label_name="Liegenschaftskataster",
    new_label_name="Liegenschaft - Liegenschaftenkataster",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Raumordnung",
    new_group_name="Raumordnung",
    old_label_name="Liegenschaftskataster",
    new_label_name="Liegenschaft - Liegenschaftenkataster",
)

# merge Liegenschaften group into Raumordnung, ...
# Gebäude
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Liegenschaften",
    new_group_name="Raumordnung",
    old_label_name="Gebäude",
    new_label_name="Liegenschaft - Grundstück und Gebäude",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Liegenschaften",
    new_group_name="Raumordnung",
    old_label_name="Gebäude",
    new_label_name="Liegenschaft - Grundstück und Gebäude",
)
# Grundstück
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Liegenschaften",
    new_group_name="Raumordnung",
    old_label_name="Grundstück",
    new_label_name="Liegenschaft - Grundstück und Gebäude",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Liegenschaften",
    new_group_name="Raumordnung",
    old_label_name="Grundstück",
    new_label_name="Liegenschaft - Grundstück und Gebäude",
)
# Satzung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Liegenschaften",
    new_group_name="Raumordnung",
    old_label_name="Satzung",
    new_label_name="Liegenschaft - Satzung",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Liegenschaften",
    new_group_name="Raumordnung",
    old_label_name="Satzung",
    new_label_name="Liegenschaft - Satzung",
)
# delete Jahresbericht
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Liegenschaften",
    old_label_name="Jahresbericht",
    node_type="all",
)
data = data_delete_concept(
    data,
    old_group_name="Liegenschaften",
    old_label_name="Jahresbericht",
    node_type="all",
)
# Merging Stadtplan into Raumordnung
# Stadtmodell 3D
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Stadtplan",
    new_group_name="Raumordnung",
    old_label_name="Stadtmodell 3D",
    new_label_name="Stadtplan",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Stadtplan",
    new_group_name="Raumordnung",
    old_label_name="Stadtmodell 3D",
    new_label_name="Stadtplan",
)
# Stadtpläne
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Stadtplan",
    new_group_name="Raumordnung",
    old_label_name="Stadtpläne",
    new_label_name="Stadtplan",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Stadtplan",
    new_group_name="Raumordnung",
    old_label_name="Stadtpläne",
    new_label_name="Stadtplan",
)
# adding two new concepts
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Raumordnung", new_label_name="Bauleitplan"
)
taxonomy = taxonomy_add_concept(
    taxonomy,
    new_group_name="Raumordnung",
    new_label_name="Raumgliederung - Straße",
)

# renaming group
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Raumordnung",
    new_group_name="Raumordnung, Raumplanung und Raumentwicklung",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)
data = data_rename_concept(
    data,
    old_group_name="Raumordnung",
    new_group_name="Raumordnung, Raumplanung und Raumentwicklung",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)

######
# Bildung
######

# Merge Schulen into Bildung
# Einrichtung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Schulen",
    new_group_name="Bildung",
    old_label_name="Einrichtung",
    new_label_name="Schule - Standort",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Schulen",
    new_group_name="Bildung",
    old_label_name="Einrichtung",
    new_label_name="Schule - Standort",
)
# Schulangebot
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Schulen",
    new_group_name="Bildung",
    old_label_name="Schulangebot",
    new_label_name="Schule - Schulangebot",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Schulen",
    new_group_name="Bildung",
    old_label_name="Schulangebot",
    new_label_name="Schule - Schulangebot",
)
# Internetanbindung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Schulen",
    new_group_name="Bildung",
    old_label_name="Internetanbindung",
    new_label_name="Schule - Internetanbindung",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Schulen",
    new_group_name="Bildung",
    old_label_name="Internetanbindung",
    new_label_name="Schule - Internetanbindung",
)
# Schuleingangsuntersuchung -> TYPO in Taxonomie!
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Schulen",
    new_group_name="Bildung",
    old_label_name="Schuleingangsuntersuchung",
    new_label_name="Schule - Schuleingangsuntersuchung",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Schulen",
    new_group_name="Bildung",
    old_label_name="Schuleingangsuntersuchung",
    new_label_name="Schule - Schuleingangsuntersuchung",
)
# Typo handling
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Schulen",
    new_group_name="Bildung",
    old_label_name="Schuleingangsunteruchungen",
    new_label_name="Schule - Schuleingangsuntersuchung",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Schulen",
    new_group_name="Bildung",
    old_label_name="Schuleingangsunteruchungen",
    new_label_name="Schule - Schuleingangsuntersuchung",
)
# Schulentwicklungsplan
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Schulen",
    new_group_name="Bildung",
    old_label_name="Schulentwicklungsplan",
    new_label_name="Schule - Schulentwicklungsplan",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Schulen",
    new_group_name="Bildung",
    old_label_name="Schulentwicklungsplan",
    new_label_name="Schule - Schulentwicklungsplan",
)
# Schülerzahl
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Schulen",
    new_group_name="Bildung",
    old_label_name="Schülerzahl",
    new_label_name="Schule - Schülerzahl",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Schulen",
    new_group_name="Bildung",
    old_label_name="Schülerzahl",
    new_label_name="Schule - Schülerzahl",
)
# Wunschschule
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Schulen",
    new_group_name="Bildung",
    old_label_name="Wunschschule",
    new_label_name="Schule - Wunschschule",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Schulen",
    new_group_name="Bildung",
    old_label_name="Wunschschule",
    new_label_name="Schule - Wunschschule",
)

# Merge Volkshochschulen into Bildung
# Teilnehmer
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Volkshochschulen",
    new_group_name="Bildung",
    old_label_name="Teilnehmer",
    new_label_name="Volkshochschule - Teilnehmerzahl",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Volkshochschulen",
    new_group_name="Bildung",
    old_label_name="Teilnehmer",
    new_label_name="Volkshochschule - Teilnehmerzahl",
)
# Teilnehmer
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Volkshochschulen",
    new_group_name="Bildung",
    old_label_name="Veranstaltung",
    new_label_name="Volkshochschule - Veranstaltung",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Volkshochschulen",
    new_group_name="Bildung",
    old_label_name="Veranstaltung",
    new_label_name="Volkshochschule - Veranstaltung",
)
# delete Information und Programm
# delete Information
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Volkshochschulen",
    old_label_name="Information",
    node_type="all",
)
data = data_delete_concept(
    data,
    old_group_name="Volkshochschulen",
    old_label_name="Information",
    node_type="all",
)
# delete Programm
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Volkshochschulen",
    old_label_name="Programm",
    node_type="all",
)
data = data_delete_concept(
    data,
    old_group_name="Volkshochschulen",
    old_label_name="Programm",
    node_type="all",
)

# Merge Musikschulen into Bildung
# Teilnehmer
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Musikschulen",
    new_group_name="Bildung",
    old_label_name="Teilnehmer",
    new_label_name="Musikschule - Teilnehmerzahl",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Musikschulen",
    new_group_name="Bildung",
    old_label_name="Teilnehmer",
    new_label_name="Musikschule - Teilnehmerzahl",
)
# Unterrichtsangebot
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Musikschulen",
    new_group_name="Bildung",
    old_label_name="Unterrichtsangebot",
    new_label_name="Musikschule - Unterrichtsangebot",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Musikschulen",
    new_group_name="Bildung",
    old_label_name="Unterrichtsangebot",
    new_label_name="Musikschule - Unterrichtsangebot",
)
# delete Jahresrechnung
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Musikschulen",
    old_label_name="Jahresrechnung",
    node_type="all",
)
data = data_delete_concept(
    data,
    old_group_name="Musikschulen",
    old_label_name="Jahresrechnung",
    node_type="all",
)

# Merge Hochschulen into Bildung
# Gebäude
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Hochschulen",
    new_group_name="Bildung",
    old_label_name="Gebäude",
    new_label_name="Hochschule - Standort",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Hochschulen",
    new_group_name="Bildung",
    old_label_name="Gebäude",
    new_label_name="Hochschule - Standort",
)
# Studierendenzahl
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Hochschulen",
    new_group_name="Bildung",
    old_label_name="Studierendenzahl",
    new_label_name="Hochschule - Studierendenzahl",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Hochschulen",
    new_group_name="Bildung",
    old_label_name="Studierendenzahl",
    new_label_name="Hochschule - Studierendenzahl",
)

# Add new label Ausbildung
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Bildung", new_label_name="Ausbildung"
)

# Merge Bibliotheken into Bildung
# Ausleihe
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Bibliotheken",
    new_group_name="Bildung",
    old_label_name="Ausleihe",
    new_label_name="Bibliothek - Ausleihe",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Bibliotheken",
    new_group_name="Bildung",
    old_label_name="Ausleihe",
    new_label_name="Bibliothek - Ausleihe",
)
# Bestand
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Bibliotheken",
    new_group_name="Bildung",
    old_label_name="Bestand",
    new_label_name="Bibliothek - Bestand",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Bibliotheken",
    new_group_name="Bildung",
    old_label_name="Bestand",
    new_label_name="Bibliothek - Bestand",
)
# Besucherzahl
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Bibliotheken",
    new_group_name="Bildung",
    old_label_name="Besucherzahl",
    new_label_name="Bibliothek - Besucherzahl",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Bibliotheken",
    new_group_name="Bildung",
    old_label_name="Besucherzahl",
    new_label_name="Bibliothek - Besucherzahl",
)
# Budget
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Bibliotheken",
    new_group_name="Bildung",
    old_label_name="Budget",
    new_label_name="Bibliothek - Budget",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Bibliotheken",
    new_group_name="Bildung",
    old_label_name="Budget",
    new_label_name="Bibliothek - Budget",
)

taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Bibliotheken",
    new_group_name="Bildung",
    old_label_name="Einrichtung",
    new_label_name="Bibliothek - Standort",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Bibliotheken",
    new_group_name="Bildung",
    old_label_name="Einrichtung",
    new_label_name="Bibliothek - Standort",
)
# delete Kennzahlen
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Bibliotheken", old_label_name="Kennzahl", node_type="all"
)
data = data_delete_concept(
    data,
    old_group_name="Bibliotheken",
    old_label_name="Kennzahl",
    node_type="all",
)
# delete Bildungsträger
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Bildungsträger",
    old_label_name="Einrichtung",
    node_type="all",
)
data = data_delete_concept(
    data,
    old_group_name="Bildungsträger",
    old_label_name="Einrichtung",
    node_type="all",
)


# Merge Kindertageseinrichtungen into Bildung
# Betreuungsplatz
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Kindertageseinrichtungen",
    new_group_name="Bildung",
    old_label_name="Betreuungsplatz",
    new_label_name="Kindertageseinrichtung - Betreuungsplatz",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Kindertageseinrichtungen",
    new_group_name="Bildung",
    old_label_name="Betreuungsplatz",
    new_label_name="Kindertageseinrichtung - Betreuungsplatz",
)
# Kindertagesstätte
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Kindertageseinrichtungen",
    new_group_name="Bildung",
    old_label_name="Kindertagesstätte",
    new_label_name="Kindertageseinrichtung - Standort",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Kindertageseinrichtungen",
    new_group_name="Bildung",
    old_label_name="Kindertagesstätte",
    new_label_name="Kindertageseinrichtung - Standort",
)

######
# Wetter
######
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wetter",
    new_group_name="Wetter",
    old_label_name="Messstelle",
    new_label_name="Messung",
    node_type="all",
)


data = data_move_concept(
    data,
    old_group_name="Wetter",
    new_group_name="Wetter",
    old_label_name="Messstelle",
    new_label_name="Messung",
)


######
# Tourismus
######
# Campingplatz
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Tourismus",
    new_group_name="Tourismus",
    old_label_name="Campingplatz",
    new_label_name="Unterkunft - Campingplatz",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Tourismus",
    new_group_name="Tourismus",
    old_label_name="Campingplatz",
    new_label_name="Unterkunft - Campingplatz",
)
# Privatunterkunft
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Tourismus",
    new_group_name="Tourismus",
    old_label_name="Privatunterkunft",
    new_label_name="Unterkunft - Privatunterkunft",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Tourismus",
    new_group_name="Tourismus",
    old_label_name="Privatunterkunft",
    new_label_name="Unterkunft - Priivatunterkunft",
)

# delete Fährverkehr and Übernachtungen as too general
# Fährverkehr
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Tourismus", old_label_name="Fährverkehr", node_type="all"
)
data = data_delete_concept(
    data, old_group_name="Tourismus", old_label_name="Fährverkehr", node_type="all"
)
# Übernachtung
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Tourismus", old_label_name="Übernachtung", node_type="all"
)
data = data_delete_concept(
    data, old_group_name="Tourismus", old_label_name="Übernachtung", node_type="all"
)

# adding two news: Herberge and Hotel
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Tourismus", new_label_name="Unterkunft - Herberge"
)
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Tourismus", new_label_name="Unterkunft - Hotel"
)


######
# Grünflächen -> Flora und Fauna
######

# deleting not merged ones
# Blumenampel
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Grünflächen",
    old_label_name="Blumenampel",
    node_type="all",
)

data = data_delete_concept(
    data, old_group_name="Grünflächen", old_label_name="Blumenampel", node_type="all"
)

# Kleingarten
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Grünflächen",
    old_label_name="Kleingarten",
    node_type="all",
)

data = data_delete_concept(
    data, old_group_name="Grünflächen", old_label_name="Kleingarten", node_type="all"
)
# Parkanlage
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Grünflächen", old_label_name="Parkanlage", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Grünflächen", old_label_name="Parkanlage", node_type="all"
)

# Brunnen merge into Bau
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Grünflächen",
    new_group_name="Bau",
    old_label_name="Brunnen",
    new_label_name="Brunnen",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Grünflächen",
    new_group_name="Bau",
    old_label_name="Brunnen",
    new_label_name="Brunnen",
)


# renaming Grünflächen into Flora und Fauna
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Grünflächen",
    new_group_name="Flora und Fauna",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)

data = data_rename_concept(
    data,
    old_group_name="Grünflächen",
    new_group_name="Flora und Fauna",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)

# restructuring second level

taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Flora und Fauna",
    new_group_name="Flora und Fauna",
    old_label_name="Baumbestand/Baumkataster",
    new_label_name="Baumbestand - Baumkataster",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Flora und Fauna",
    new_group_name="Flora und Fauna",
    old_label_name="Baumbestand/Baumkataster",
    new_label_name="Baumbestand - Baumkataster",
)
# Baumfällung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Flora und Fauna",
    new_group_name="Flora und Fauna",
    old_label_name="Baumfällung",
    new_label_name="Baumbestand - Baumfällung",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Flora und Fauna",
    new_group_name="Flora und Fauna",
    old_label_name="Baumfällung",
    new_label_name="Baumbestand - Baumfällung",
)
# add Baumstandort
taxonomy = taxonomy_add_concept(
    taxonomy,
    new_group_name="Flora und Fauna",
    new_label_name="Baumbestand - Baumstandort",
)

# Restructuring Flora und Fauna - Fläche
# Biotopfläche
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Flora und Fauna",
    new_group_name="Flora und Fauna",
    old_label_name="Biotopfläche",
    new_label_name="Fläche - Biotopfläche",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Flora und Fauna",
    new_group_name="Flora und Fauna",
    old_label_name="Biotopfläche",
    new_label_name="Fläche - Biotopfläche",
)
# Jagdbezirk
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Flora und Fauna",
    new_group_name="Flora und Fauna",
    old_label_name="Jagdbezirk",
    new_label_name="Fläche - Jagdbezirk",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Flora und Fauna",
    new_group_name="Flora und Fauna",
    old_label_name="Jagdbezirk",
    new_label_name="Fläche - Jagdbezirk",
)
# Hundewiese
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Flora und Fauna",
    new_group_name="Flora und Fauna",
    old_label_name="Hundewiese",
    new_label_name="Fläche - Hundewiese",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Flora und Fauna",
    new_group_name="Flora und Fauna",
    old_label_name="Hundewiese",
    new_label_name="Fläche - Hundewiese",
)
# Naturschutz -> Naturschutzgebiet
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Flora und Fauna",
    new_group_name="Flora und Fauna",
    old_label_name="Naturschutz",
    new_label_name="Fläche - Naturschutzgebiet",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Flora und Fauna",
    new_group_name="Flora und Fauna",
    old_label_name="Naturschutz",
    new_label_name="Fläche - Naturschutzgebiet",
)
# Ausgleichsfläche
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Flora und Fauna",
    new_group_name="Flora und Fauna",
    old_label_name="Ausgleichsfläche",
    new_label_name="Fläche - Ausgleichsfläche",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Flora und Fauna",
    new_group_name="Flora und Fauna",
    old_label_name="Ausgleichsfläche",
    new_label_name="Fläche - Ausgleichsfläche",
)
# Waldfläche
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Flora und Fauna",
    new_group_name="Flora und Fauna",
    old_label_name="Waldfläche",
    new_label_name="Fläche - Waldfläche",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Flora und Fauna",
    new_group_name="Flora und Fauna",
    old_label_name="Waldfläche",
    new_label_name="Fläche - Waldfläche",
)
# Grünflächen
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Flora und Fauna",
    new_group_name="Flora und Fauna",
    old_label_name="Grünfläche/Grünflächenkataster",
    new_label_name="Fläche - Grünfläche und Grünflächenkataster",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Flora und Fauna",
    new_group_name="Flora und Fauna",
    old_label_name="Grünfläche/Grünflächenkataster",
    new_label_name="Fläche - Grünfläche und Grünflächenkataster",
)

# Merge Gewässer into Flora und Fauna
# Gewässer - Pegelstand
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Gewässer",
    new_group_name="Flora und Fauna",
    old_label_name="Pegelstand",
    new_label_name="Gewässer - Pegelstand",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Gewässer",
    new_group_name="Flora und Fauna",
    old_label_name="Pegelstand",
    new_label_name="Gewässer - Pegelstand",
)
# Gewässer - Wasserfläche
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Gewässer",
    new_group_name="Flora und Fauna",
    old_label_name="Wasserfläche",
    new_label_name="Gewässer - Wasserfläche",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Gewässer",
    new_group_name="Flora und Fauna",
    old_label_name="Wasserfläche",
    new_label_name="Gewässer - Wasserfläche",
)


######
# Kultur
######

# rename Lehr und Wanderpfad -> Lehrpfad
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Kultur",
    new_group_name="Kultur",
    old_label_name="Lehr und Wanderpfade",
    new_label_name="Lehrpfad",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Kultur",
    new_group_name="Kultur",
    old_label_name="Lehr und Wanderpfade",
    new_label_name="Lehrpfad",
)

# deleting generic Kultur Bezeichnungen (can be sorted into the other categories again)
# Besucherzahl
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Kultur", old_label_name="Besucherzahl", node_type="all"
)
data = data_delete_concept(
    data, old_group_name="Kultur", old_label_name="Besucherzahl", node_type="all"
)
# Förderung
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Kultur", old_label_name="Förderung", node_type="all"
)
data = data_delete_concept(
    data, old_group_name="Kultur", old_label_name="Förderung", node_type="all"
)
# Information
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Kultur", old_label_name="Information", node_type="all"
)
data = data_delete_concept(
    data, old_group_name="Kultur", old_label_name="Information", node_type="all"
)
# Veranstaltung
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Kultur", old_label_name="Veranstaltung", node_type="all"
)
data = data_delete_concept(
    data, old_group_name="Kultur", old_label_name="Veranstaltung", node_type="all"
)
# Merge Museen into Kultur
# Besucherzahl
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Museen",
    new_group_name="Kultur",
    old_label_name="Besucherzahl",
    new_label_name="Museum - Besucherzahl",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Museen",
    new_group_name="Kultur",
    old_label_name="Besucherzahl",
    new_label_name="Museum - Besucherzahl",
)
# Einrichtung -> Standort
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Museen",
    new_group_name="Kultur",
    old_label_name="Einrichtung",
    new_label_name="Museum - Standort",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Museen",
    new_group_name="Kultur",
    old_label_name="Einrichtung",
    new_label_name="Museum - Standort",
)

# Merging Theater into Kultur
# Besucherzahl
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Theater",
    new_group_name="Kultur",
    old_label_name="Besucherzahl",
    new_label_name="Theater - Besucherzahl",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Theater",
    new_group_name="Kultur",
    old_label_name="Besucherzahl",
    new_label_name="Theater - Besucherzahl",
)
# Veranstaltung -> Programm
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Theater",
    new_group_name="Kultur",
    old_label_name="Veranstaltung",
    new_label_name="Theater - Programm",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Theater",
    new_group_name="Kultur",
    old_label_name="Veranstaltung",
    new_label_name="Theater - Programm",
)

# Merge Friedhöfe into Kultur
# Einrichtung -> Standort
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Friedhöfe",
    new_group_name="Kultur",
    old_label_name="Einrichtung",
    new_label_name="Friedhof - Standort",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Friedhöfe",
    new_group_name="Kultur",
    old_label_name="Einrichtung",
    new_label_name="Friedhof - Standort",
)
# Grabstätte
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Friedhöfe",
    new_group_name="Kultur",
    old_label_name="Grabstätte",
    new_label_name="Friedhof - Grabstätte",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Friedhöfe",
    new_group_name="Kultur",
    old_label_name="Grabstätte",
    new_label_name="Friedhof - Programm",
)
# deleting Ehrengrab
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Friedhöfe", old_label_name="Ehrengrab", node_type="all"
)
data = data_delete_concept(
    data, old_group_name="Friedhöfe", old_label_name="Ehrengrab", node_type="all"
)

# adding general Veranstaltung category
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Kultur", new_label_name="Veranstaltung - Angebot"
)
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Kultur", new_label_name="Veranstaltung - Besucherzahl"
)

# Merging Kirche etc. in Kultur
# Kirche, Kapelle und Kloster
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Externe Infrastruktur",
    new_group_name="Kultur",
    old_label_name="Kirche, Kapelle und Kloster",
    new_label_name="Kirche, Kapelle und Kloster",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Externe Infrastruktur",
    new_group_name="Kultur",
    old_label_name="Kirche, Kapelle und Kloster",
    new_label_name="Kirche, Kapelle und Kloster",
)
# Religionszugehörigkeit
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Bevölkerung",
    new_group_name="Bevölkerungsstruktur",
    old_label_name="Religionszugehörigkeit",
    new_label_name="Religionszugehörigkeit",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Bevölkerung",
    new_group_name="Bevölkerungsstruktur",
    old_label_name="Religionszugehörigkeit",
    new_label_name="Religionszugehörigkeit",
)


#####
# Bau
#####

# delete not necessary ones
# Bauzeichnung
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Bau", old_label_name="Bauzeichnung", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Bau", old_label_name="Bauzeichnung", node_type="all"
)


# Gebäude
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Bau", old_label_name="Gebäude", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Bau", old_label_name="Gebäude", node_type="all"
)

# Merge Tiefbau into Bau
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Tiefbau",
    new_group_name="Bau",
    old_label_name="Geschäftsbericht",
    new_label_name="Tiefbau",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Tiefbau",
    new_group_name="Bau",
    old_label_name="Geschäftsbericht",
    new_label_name="Tiefbau",
)

# merge Infrastruktur - Baustelle into Bau
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Infrastruktur",
    new_group_name="Bau",
    old_label_name="Baustelle",
    new_label_name="Baustelle",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Infrastruktur",
    new_group_name="Bau",
    old_label_name="Baustelle",
    new_label_name="Baustelle",
)

# Merge Individualverkehr - Baustelle into Bau
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Individualverkehr",
    new_group_name="Bau",
    old_label_name="Baustelle",
    new_label_name="Baustelle",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Individualverkehr",
    new_group_name="Bau",
    old_label_name="Baustelle",
    new_label_name="Baustelle",
)

# Rename Bau - Grundstückbewertung to Grundstücksbewertung
taxonomy = taxonomy_rename_concept(
    taxonomy=taxonomy,
    old_group_name="Bau",
    new_group_name="Bau",
    old_label_name="Grundstückbewertung",
    new_label_name="Grundstücksbewertung",
    node_type="all",
)

######
# Abfallentsorgung
######

# rename Abfallwirtschaft -> Abfallentsorgung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Abfallwirtschaft",
    new_group_name="Abfallentsorgung",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)

data = data_rename_concept(
    data,
    old_group_name="Abfallwirtschaft",
    new_group_name="Abfallentsorgung",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)

# merge Infrastruktur - Straßenreinigung into Abfallentsorgung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Infrastruktur",
    new_group_name="Abfallentsorgung",
    old_label_name="Straßenreinigung",
    new_label_name="Straßenreinigung",
    node_type="all",
)

# delete Betriebe
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Abfallentsorgung",
    old_label_name="Betrieb",
    node_type="all",
)
data = data_delete_concept(
    data, old_group_name="Abfallentsorgung", old_label_name="Betrieb", node_type="all"
)

# delete Gremium
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Abfallentsorgung",
    old_label_name="Gremium",
    node_type="all",
)
data = data_delete_concept(
    data, old_group_name="Abfallentsorgung", old_label_name="Gremium", node_type="all"
)

######
# Bürgerservice
######

# move Hundekottüte
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Flora und Fauna",
    new_group_name="Bürgerservice",
    old_label_name="Hundekottüte",
    new_label_name="Hundekottüte",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Flora und Fauna",
    new_group_name="Bürgerservice",
    old_label_name="Hundekottüte",
    new_label_name="Hundekottüte",
)

# rename Produkte -> Dienstleistung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Bürgerservice",
    new_group_name="Bürgerservice",
    old_label_name="Produkt",
    new_label_name="Dienstleistung",
    node_type="all",
)

######
# Gesundheit
######

# rename Gesundheitseinrichtungen -> Gesundheit
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Gesundheitseinrichtungen",
    new_group_name="Gesundheit",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)
data = data_rename_concept(
    data,
    old_group_name="Gesundheitseinrichtungen",
    new_group_name="Gesundheit",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)

# remove Bad
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Gesundheit", old_label_name="Bad", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Gesundheit", old_label_name="Bad", node_type="all"
)

# move Öffentliche Toiletten into Gesundheit
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Infrastruktur",
    new_group_name="Gesundheit",
    old_label_name="Öffentliche Toilette",
    new_label_name="Öffentliche Toilette",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Infrastruktur",
    new_group_name="Gesundheit",
    old_label_name="Öffentliche Toilette",
    new_label_name="Öffentliche Toilette",
)

# Arzt
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Gesundheit", new_label_name="Arzt"
)

# Gesundheitsberichtserstattung
taxonomy = taxonomy_add_concept(
    taxonomy,
    new_group_name="Gesundheit",
    new_label_name="Gesundheitsberichtserstattung",
)

# Arzt
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Gesundheit", new_label_name="Infektion"
)


#####
# Verkehr
#####

# delete not merged
# Adresse
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Infrastruktur", old_label_name="Adresse", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Infrastruktur", old_label_name="Adresse", node_type="all"
)
# Brücke
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Infrastruktur", old_label_name="Brücke", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Infrastruktur", old_label_name="Brücke", node_type="all"
)
# Straße
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Infrastruktur", old_label_name="Straße", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Infrastruktur", old_label_name="Straße", node_type="all"
)
# WLAN und Mobilfunk
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Infrastruktur",
    old_label_name="WLAN und Mobilfunk",
    node_type="all",
)

data = data_delete_concept(
    data,
    old_group_name="Infrastruktur",
    old_label_name="WLAN und Mobilfunk",
    node_type="all",
)

# Fußgängerzone
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Infrastruktur",
    new_group_name="Infrastruktur",
    old_label_name="Fußgängerzone",
    new_label_name="Fußverkehr - Fußgängerzone",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Infrastruktur",
    new_group_name="Infrastruktur",
    old_label_name="Fußgängerzone",
    new_label_name="Fußverkehr - Fußgängerzone",
)
# Laufstrecke
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Infrastruktur",
    new_group_name="Infrastruktur",
    old_label_name="Laufstrecke",
    new_label_name="Fußverkehr - Lauf und Wanderstrecke",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Infrastruktur",
    new_group_name="Infrastruktur",
    old_label_name="Laufstrecke",
    new_label_name="Fußverkehr - Lauf und Wanderstrecke",
)

# add new Gehweg (Geh und Radweg too broad) and delte Geh und Radweg
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Infrastruktur", new_label_name="Fußverkehr - Gehweg"
)

# delete
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Infrastruktur",
    old_label_name="Geh und Radweg",
    node_type="all",
)
data = data_delete_concept(
    data,
    old_group_name="Infrastruktur",
    old_label_name="Geh und Radweg",
    node_type="all",
)

# Flughafen
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Infrastruktur",
    new_group_name="Infrastruktur",
    old_label_name="Flughafen",
    new_label_name="Flugverkehr - Flughafen",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Infrastruktur",
    new_group_name="Infrastruktur",
    old_label_name="Flughafen",
    new_label_name="Flugverkehr - Flughafen",
)
# merge from Individualverkehr
# delete not merged from Individualverkehr
# Kennzahl
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Individualverkehr",
    old_label_name="Kennzahl",
    node_type="all",
)

data = data_delete_concept(
    data, old_group_name="Individualverkehr", old_label_name="Kennzahl", node_type="all"
)
# KFZ Bestand
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Individualverkehr",
    old_label_name="KFZ Bestand",
    node_type="all",
)

data = data_delete_concept(
    data,
    old_group_name="Individualverkehr",
    old_label_name="KFZ Bestand",
    node_type="all",
)
# Lärm
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Individualverkehr", old_label_name="Lärm", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Individualverkehr", old_label_name="Lärm", node_type="all"
)
# Messstelle
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Individualverkehr",
    old_label_name="Messstelle",
    node_type="all",
)

data = data_delete_concept(
    data,
    old_group_name="Individualverkehr",
    old_label_name="Messstelle",
    node_type="all",
)
# Schwerlastverkehr
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Individualverkehr",
    old_label_name="Schwerlastverkehr",
    node_type="all",
)

data = data_delete_concept(
    data,
    old_group_name="Individualverkehr",
    old_label_name="Schwerlastverkehr",
    node_type="all",
)


# Flugbewegung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Individualverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Flugbewegung",
    new_label_name="Flugverkehr - Flugbewegung",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Individualverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Flugbewegung",
    new_label_name="Flugverkehr - Flugbewegung",
)

# Unfall
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Individualverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Unfall",
    new_label_name="Unfall",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Individualverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Unfall",
    new_label_name="Unfall",
)
# Unfall
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Individualverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Sondernutzung",
    new_label_name="Sondernutzung",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Individualverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Sondernutzung",
    new_label_name="Sondernutzung",
)
# Fracht
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Individualverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Fracht",
    new_label_name="Schiff und Fährverkehr - Fracht",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Individualverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Fracht",
    new_label_name="Schiff und Fährverkehr - Fracht",
)
# Fracht 2.0
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Fährverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Fracht",
    new_label_name="Schiff und Fährverkehr - Fracht",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Fährverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Fracht",
    new_label_name="Schiff und Fährverkehr - Fracht",
)

# Schiffsanlegestelle
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Infrastruktur",
    new_group_name="Infrastruktur",
    old_label_name="Schiffsanlegestelle",
    new_label_name="Schiff und Fährverkehr - Anlegestelle",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Infrastruktur",
    new_group_name="Infrastruktur",
    old_label_name="Schiffsanlegestelle",
    new_label_name="Schiff und Fährverkehr - Anlegestelle",
)
# Passagier
taxonomy_add_concept(
    taxonomy,
    new_group_name="Infrastruktur",
    new_label_name="Schiff und Fährverkehr - Passagier",
)
# ÖPNV

# delete Befragung
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="ÖPNV", old_label_name="Befragung", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="ÖPNV", old_label_name="Befragung", node_type="all"
)

# delete Haltestelle
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="ÖPNV", old_label_name="Haltestelle", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="ÖPNV", old_label_name="Haltestelle", node_type="all"
)
# delete Verkehrsnetz
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="ÖPNV", old_label_name="Verkehrsnetz", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="ÖPNV", old_label_name="Verkehrsnetz", node_type="all"
)

# Aufzug und Rolltreppe
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="ÖPNV",
    new_group_name="Infrastruktur",
    old_label_name="Aufzug und Rolltreppe",
    new_label_name="ÖPNV - Aufzug und Rolltreppe",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="ÖPNV",
    new_group_name="Infrastruktur",
    old_label_name="Aufzug und Rolltreppe",
    new_label_name="ÖPNV - Aufzug und Rolltreppe",
)
# Fahrgastzahl
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="ÖPNV",
    new_group_name="Infrastruktur",
    old_label_name="Fahrgastzahl",
    new_label_name="ÖPNV - Fahrgastzahl",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="ÖPNV",
    new_group_name="Infrastruktur",
    old_label_name="Fahrgastzahl",
    new_label_name="ÖPNV - Fahrgastzahl",
)
# Liniennetz
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="ÖPNV",
    new_group_name="Infrastruktur",
    old_label_name="Liniennetz",
    new_label_name="ÖPNV - Liniennetz",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="ÖPNV",
    new_group_name="Infrastruktur",
    old_label_name="Liniennetz",
    new_label_name="ÖPNV - Liniennetz",
)
# Sollfahrdaten
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="ÖPNV",
    new_group_name="Infrastruktur",
    old_label_name="Sollfahrdaten",
    new_label_name="ÖPNV - Sollfahrdaten",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="ÖPNV",
    new_group_name="Infrastruktur",
    old_label_name="Sollfahrdaten",
    new_label_name="ÖPNV - Sollfahrdaten",
)
# Vertriebsstelle
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="ÖPNV",
    new_group_name="Infrastruktur",
    old_label_name="Vertriebsstelle",
    new_label_name="ÖPNV - Vertriebsstelle",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="ÖPNV",
    new_group_name="Infrastruktur",
    old_label_name="Vertriebsstelle",
    new_label_name="ÖPNV - Vertriebsstelle",
)


# Auto und Schwerlastenverkehr
# Elektrotankstelle
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Infrastruktur",
    new_group_name="Infrastruktur",
    old_label_name="Elektrotankstelle",
    new_label_name="KFZ - Elektrotankstelle",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Infrastruktur",
    new_group_name="Infrastruktur",
    old_label_name="Elektrotankstelle",
    new_label_name="KFZ - Elektrotankstelle",
)
# Tankstelle
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Infrastruktur",
    new_group_name="Infrastruktur",
    old_label_name="Tankstelle",
    new_label_name="KFZ - Tankstelle",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Infrastruktur",
    new_group_name="Infrastruktur",
    old_label_name="Tankstelle",
    new_label_name="KFZ - Tankstelle",
)
# Parkplatz
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Infrastruktur",
    new_group_name="Infrastruktur",
    old_label_name="Parkplatz",
    new_label_name="KFZ - Parkplatz",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Infrastruktur",
    new_group_name="Infrastruktur",
    old_label_name="Parkplatz",
    new_label_name="KFZ - Parkplatz",
)

# Autobahnanbindung -> Autobahn
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Infrastruktur",
    new_group_name="Infrastruktur",
    old_label_name="Autobahnanbindung",
    new_label_name="KFZ - Autobahn",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Infrastruktur",
    new_group_name="Infrastruktur",
    old_label_name="Autobahnanbindung",
    new_label_name="KFZ - Autobahn",
)
# Taxi -> Taxistand
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Individualverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Taxi",
    new_label_name="KFZ - Taxistand",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Individualverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Taxi",
    new_label_name="KFZ - Taxistand",
)
# Bußgeld
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Individualverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Bußgeld",
    new_label_name="KFZ - Bußgeld",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Individualverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Bußgeld",
    new_label_name="KFZ - Bußgeld",
)
# Carsharing
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Individualverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Carsharing",
    new_label_name="KFZ - Carsharing",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Individualverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Carsharing",
    new_label_name="KFZ - Carsharing",
)
# Fahrzeugzulassung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Individualverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Fahrzeugzulassung",
    new_label_name="KFZ - Fahrzeugzulassung",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Individualverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Fahrzeugzulassung",
    new_label_name="KFZ - Fahrzeugzulassung",
)
# Straßenverkehr -> Verkehrsaufkommen
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Individualverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Straßenverkehr",
    new_label_name="KFZ - Verkehrsaufkommen",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Individualverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Straßenverkehr",
    new_label_name="KFZ - Verkehrsaufkommen",
)

# add Messung
taxonomy = taxonomy_add_concept(
    taxonomy,
    new_group_name="Infrastruktur",
    new_label_name="KFZ - Messung",
)
# Radverkehr (merge Radverkehr into Infrastruktur)

# delete Bürgerbeteiligung
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Radverkehr",
    old_label_name="Bürgerbeteiligung",
    node_type="all",
)
data = data_delete_concept(
    data,
    old_group_name="Radverkehr",
    old_label_name="Bürgerbeteiligung",
    node_type="all",
)
# delete Fahhrad
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Radverkehr", old_label_name="Fahrrad", node_type="all"
)
data = data_delete_concept(
    data,
    old_group_name="Radverkehr",
    old_label_name="Fahrrad",
    node_type="all",
)
# delete Förderung
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Radverkehr", old_label_name="Förderung", node_type="all"
)
data = data_delete_concept(
    data,
    old_group_name="Radverkehr",
    old_label_name="Förderung",
    node_type="all",
)
# Ladestation
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Radverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Ladestation",
    new_label_name="Radverkehr - Ladestation",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Radverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Ladestation",
    new_label_name="Radverkehr - Ladestation",
)
# Messstelle -> Messung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Radverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Messstelle",
    new_label_name="Radverkehr - Messung",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Radverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Messstelle",
    new_label_name="Radverkehr - Messung",
)
# Stellplatz -> Abstellplatz
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Radverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Stellplatz",
    new_label_name="Radverkehr - Abstellplatz",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Radverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Stellplatz",
    new_label_name="Radverkehr - Abstellplatz",
)
# Radroute -> Radweg und Radroute
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Radverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Radroute",
    new_label_name="Radverkehr - Radweg und Radroute",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Radverkehr",
    new_group_name="Infrastruktur",
    old_label_name="Radroute",
    new_label_name="Radverkehr - Radweg und Radroute",
)
# Fahrradstraße -> Radweg und Radroute
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Infrastruktur",
    new_group_name="Infrastruktur",
    old_label_name="Fahrradstraße",
    new_label_name="Radverkehr - Radweg und Radroute",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Infrastruktur",
    new_group_name="Infrastruktur",
    old_label_name="Fahrradstraße",
    new_label_name="Radverkehr - Radweg und Radroute",
)
# add two new concepts
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Infrastruktur", new_label_name="Radverkehr - Verleih"
)
taxonomy = taxonomy_add_concept(
    taxonomy,
    new_group_name="Infrastruktur",
    new_label_name="Radverkehr - Verkehrsteilnehmer",
)

# rename Infrastruktur -> Verkehr
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Infrastruktur",
    new_group_name="Verkehr",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)
data = data_rename_concept(
    data,
    old_group_name="Infrastruktur",
    new_group_name="Verkehr",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)

#####
# Wirtschaft
#####

# delete not merged ones
# Arbeit
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Wirtschaft", old_label_name="Arbeit", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Wirtschaft", old_label_name="Arbeit", node_type="all"
)
# Meldung
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Wirtschaft", old_label_name="Meldung", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Wirtschaft", old_label_name="Meldung", node_type="all"
)
# Unternehmen
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Wirtschaft", old_label_name="Unternehmen", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Wirtschaft", old_label_name="Unternehmen", node_type="all"
)


# merging Bürfofläche und Industrie und Gewerbefläche
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wirtschaft",
    new_group_name="Wirtschaft",
    old_label_name="Bürofläche",
    new_label_name="Büro, Industrie und Gewerbefläche",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wirtschaft",
    new_group_name="Wirtschaft",
    old_label_name="Bürofläche",
    new_label_name="Büro, Industrie und Gewerbefläche",
)

taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wirtschaft",
    new_group_name="Wirtschaft",
    old_label_name="Industrie und Gewerbefläche",
    new_label_name="Büro, Industrie und Gewerbefläche",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wirtschaft",
    new_group_name="Wirtschaft",
    old_label_name="Industrie und Gewerbefläche",
    new_label_name="Büro, Industrie und Gewerbefläche",
)
# add new
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Wirtschaft", new_label_name="Gewerbeanmeldung"
)

# merge in pendler
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Individualverkehr",
    new_group_name="Wirtschaft",
    old_label_name="Pendler",
    new_label_name="Berufspendler",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Individualverkehr",
    new_group_name="Wirtschaft",
    old_label_name="Pendler",
    new_label_name="Berufspendler",
)
# merge in parts from Externe Infrastruktur
# Postfiliale
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Externe Infrastruktur",
    new_group_name="Wirtschaft",
    old_label_name="Postfiliale",
    new_label_name="Dienstleistung - Postfiliale",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Externe Infrastruktur",
    new_group_name="Wirtschaft",
    old_label_name="Postfiliale",
    new_label_name="Dienstleistung - Postfiliale",
)
# Weihnachtsmarkt
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Externe Infrastruktur",
    new_group_name="Wirtschaft",
    old_label_name="Weihnachtsmarkt",
    new_label_name="Dienstleistung - Weihnachtsmarkt",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Externe Infrastruktur",
    new_group_name="Wirtschaft",
    old_label_name="Weihnachtsmarkt",
    new_label_name="Dienstleistung - Weihnachtsmarkt",
)
# Einzelhandel
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Externe Infrastruktur",
    new_group_name="Wirtschaft",
    old_label_name="Einzelhandel",
    new_label_name="Dienstleistung - Einzelhandel",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Externe Infrastruktur",
    new_group_name="Wirtschaft",
    old_label_name="Einzelhandel",
    new_label_name="Dienstleistung - Einzelhandel",
)
# Wochenmarkt
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Externe Infrastruktur",
    new_group_name="Wirtschaft",
    old_label_name="Wochenmarkt",
    new_label_name="Dienstleistung - Wochenmarkt",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Externe Infrastruktur",
    new_group_name="Wirtschaft",
    old_label_name="Wochenmarkt",
    new_label_name="Dienstleistung - Wochenmarkt",
)
# deleting not assigned categories
# Einkaufsführer
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Externe Infrastruktur",
    old_label_name="Einkaufsführer",
    node_type="all",
)
data = data_delete_concept(
    data,
    old_group_name="Externe Infrastruktur",
    old_label_name="Einkaufsführer",
    node_type="all",
)
# Markt
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Externe Infrastruktur",
    old_label_name="Markt",
    node_type="all",
)
data = data_delete_concept(
    data,
    old_group_name="Externe Infrastruktur",
    old_label_name="Markt",
    node_type="all",
)
# Öffnungszeit
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Externe Infrastruktur",
    old_label_name="Öffnungszeit",
    node_type="all",
)
data = data_delete_concept(
    data,
    old_group_name="Externe Infrastruktur",
    old_label_name="Öffnungszeit",
    node_type="all",
)
# adding Handwerk
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Wirtschaft", new_label_name="Dienstleistung - Handwerk"
)
# adding Beschäftigung
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Wirtschaft", new_label_name="Beschäftigung"
)
# adding Arbeitslosigkeit
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Wirtschaft", new_label_name="Arbeitslosigkeit"
)

# merge Öffentliche Wirtschaft into Wirtschaft
# Ausschreibung Vergabe
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Öffentliche Wirtschaft",
    new_group_name="Wirtschaft",
    old_label_name="Ausschreibung Vergabe",
    new_label_name="Beteiligung an Öffentlicher Wirtschaft - Ausschreibung und Vergabe",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Öffentliche Wirtschaft",
    new_group_name="Wirtschaft",
    old_label_name="Ausschreibung Vergabe",
    new_label_name="Beteiligung an Öffentlicher Wirtschaft - Ausschreibung und Vergabe",
)
# Beteiligung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Öffentliche Wirtschaft",
    new_group_name="Wirtschaft",
    old_label_name="Beteiligung",
    new_label_name="Beteiligung an Öffentlicher Wirtschaft - Beteiligung",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Öffentliche Wirtschaft",
    new_group_name="Wirtschaft",
    old_label_name="Beteiligung",
    new_label_name="Beteiligung an Öffentlicher Wirtschaft - Beteiligung",
)

# Co-Working
taxonomy = taxonomy_add_concept(
    taxonomy, new_group_name="Wirtschaft", new_label_name="Co-Working"
)


######
# politische Partizipation
######

# creating new group and merging others into it
# Bürgermeister
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Politische Vertretung",
    new_group_name="Politische Partizipation",
    old_label_name="Bürgermeister",
    new_label_name="Politische Vertretung - Bürgermeister",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Politische Vertretung",
    new_group_name="Politische Partizipation",
    old_label_name="Bürgermeister",
    new_label_name="Politische Vertretung - Bürgermeister",
)
# Gremium
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Politische Vertretung",
    new_group_name="Politische Partizipation",
    old_label_name="Gremium",
    new_label_name="Politische Vertretung - Gremium",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Politische Vertretung",
    new_group_name="Politische Partizipation",
    old_label_name="Gremium",
    new_label_name="Politische Vertretung - Gremium",
)
# Mandatsträger
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Politische Vertretung",
    new_group_name="Politische Partizipation",
    old_label_name="Mandatsträger",
    new_label_name="Politische Vertretung - Mandatsträger",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Politische Vertretung",
    new_group_name="Politische Partizipation",
    old_label_name="Mandatsträger",
    new_label_name="Politische Vertretung - Mandatsträger",
)
# merging Bürgerbeteiligung into Politische Partizipation
# Bürgerentscheid
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Bürgerbeteiligung",
    new_group_name="Politische Partizipation",
    old_label_name="Bürgerentscheid",
    new_label_name="Bürgerbeteiligung - Bürgerentscheid",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Bürgerbeteiligung",
    new_group_name="Politische Partizipation",
    old_label_name="Bürgerentscheid",
    new_label_name="Bürgerbeteiligung - Bürgerentscheid",
)
# Bürgerhaushalt
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Bürgerbeteiligung",
    new_group_name="Politische Partizipation",
    old_label_name="Bürgerhaushalt",
    new_label_name="Bürgerbeteiligung - Bürgerhaushalt",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Bürgerbeteiligung",
    new_group_name="Politische Partizipation",
    old_label_name="Bürgerhaushalt",
    new_label_name="Bürgerbeteiligung - Bürgerhaushalt",
)
# Information -> Entwicklung und Information
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Bürgerbeteiligung",
    new_group_name="Politische Partizipation",
    old_label_name="Information",
    new_label_name="Bürgerbeteiligung - Entwicklung und Information",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Bürgerbeteiligung",
    new_group_name="Politische Partizipation",
    old_label_name="Information",
    new_label_name="Bürgerbeteiligung - Entwicklung und Informmation",
)
# Umfrage
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Bürgerbeteiligung",
    new_group_name="Politische Partizipation",
    old_label_name="Umfrage",
    new_label_name="Bürgerbeteiligung - Umfrage",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Bürgerbeteiligung",
    new_group_name="Politische Partizipation",
    old_label_name="Umfrage",
    new_label_name="Bürgerbeteiligung - Umfrage",
)
# merge Wahlen into Politische Partizipation
# Kandidatenliste
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Kandidatenliste",
    new_label_name="Wahl - Kandidatenliste",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Kandidatenliste",
    new_label_name="Wahl - Kandidatenliste",
)
# Straßen -> Straßenverzeichnis
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Straße",
    new_label_name="Wahl - Straßenverzeichnis",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Straße",
    new_label_name="Wahl - Straßenverzeichnis",
)
# merge three labels of Kommunalwahl
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Kommunalwahl",
    new_label_name="Wahl - Kommunalwahl",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Kommunalwahl",
    new_label_name="Wahl - Kommunalwahl",
)
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlbeteiligung Kommunalwahl",
    new_label_name="Wahl - Kommunalwahl",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlbeteiligung Kommunalwahl",
    new_label_name="Wahl - Kommunalwahl",
)
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlergebnis Kommunalwahl",
    new_label_name="Wahl - Kommunalwahl",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlergebnis Kommunalwahl",
    new_label_name="Wahl - Kommunalwahl",
)
# merge Wahlkreis und Wahlbezirk
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlbezirk",
    new_label_name="Wahl - Wahlkreis und Wahlbezirk",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlbezirk",
    new_label_name="Wahl - Wahlkreis und Wahlbezirk",
)
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlkreis",
    new_label_name="Wahl - Wahlkreis und Wahlbezirk",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlkreis",
    new_label_name="Wahl - Wahlkreis und Wahlbezirk",
)
# Wahllokal
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahllokal",
    new_label_name="Wahl - Wahllokal",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahllokal",
    new_label_name="Wahl - Wahllokal",
)
# Wahlergebnis Verbundwahl -> Verbundwahl
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlergebnis Verbundwahl",
    new_label_name="Wahl - Verbundwahl",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlergebnis Verbundwahl",
    new_label_name="Wahl - Verbundwahl",
)
# Beiratswahl
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlergebnis Beiratswahl",
    new_label_name="Wahl - Beiratswahl",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlergebnis Beiratswahl",
    new_label_name="Wahl - Beiratswahl",
)
# merging Wahlerbenis und Wahlbeteiligung
# Bundestagswahl
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlbeteiligung Bundestagswahl",
    new_label_name="Wahl - Bundestagswahl",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlbeteiligung Bundestagswahl",
    new_label_name="Wahl - Bundestagswahl",
)
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlergebnis Bundestagswahl",
    new_label_name="Wahl - Bundestagswahl",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlergebnis Bundestagswahl",
    new_label_name="Wahl - Bundestagswahl",
)
# Europawahl
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlergebnis Europawahl",
    new_label_name="Wahl - Europawahl",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlergebnis Europawahl",
    new_label_name="Wahl - Europawahl",
)
# Landtagswahl
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlergebnis Landtagswahl",
    new_label_name="Wahl - Landtagswahl",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wahlen",
    new_group_name="Politische Partizipation",
    old_label_name="Wahlergebnis Landtagswahl",
    new_label_name="Wahl - Landtagswahl",
)
# delete Testdatensätze
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Wahlen", old_label_name="Testdatensatz", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Wahlen", old_label_name="Testdatensatz", node_type="all"
)
# merge Vereine und Verbände into Politische PArtizipation
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Vereine, Verbände",
    new_group_name="Politische Partizipation",
    old_label_name="Einrichtung",
    new_label_name="Verband",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Vereine, Verbände",
    new_group_name="Politische Partizipation",
    old_label_name="Einrichtung",
    new_label_name="Verband",
)

######
# Soziale Hilfe
######

# merge in Senioren
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Senioren",
    new_group_name="Soziale Hilfe",
    old_label_name="Einrichtung",
    new_label_name="Pflege",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Senioren",
    new_group_name="Soziale Hilfe",
    old_label_name="Einrichtung",
    new_label_name="Pflege",
)

# Behindertenwohheim
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Soziale Hilfen",
    new_group_name="Soziale Hilfe",
    old_label_name="Behindertenwohnheim",
    new_label_name="Behinderung - Behindertenwohnheim",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Soziale Hilfen",
    new_group_name="Soziale Hilfe",
    old_label_name="Behindertenwohnheim",
    new_label_name="Behinderung - Behindertenwohnheim",
)

# Behinderung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Bevölkerung",
    new_group_name="Soziale Hilfe",
    old_label_name="Menschen mit Behinderung",
    new_label_name="Behinderung - Menschen mit Behinderung",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Bevölkerung",
    new_group_name="Soziale Hilfe",
    old_label_name="Menschen mit Behinderung",
    new_label_name="Behinderung - Menschen mit Behinderung",
)

# Flucht
# Asylwerber
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Soziale Hilfen",
    new_group_name="Soziale Hilfe",
    old_label_name="Asylwerber",
    new_label_name="Flucht - Asylbewerber",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Soziale Hilfen",
    new_group_name="Soziale Hilfe",
    old_label_name="Asylwerber",
    new_label_name="Flucht - Asylbewerber",
)
# Flüchtlingszahl
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Bevölkerung",
    new_group_name="Soziale Hilfe",
    old_label_name="Flüchtlingszahl",
    new_label_name="Flucht - Flüchtlingszahl",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Bevölkerung",
    new_group_name="Soziale Hilfe",
    old_label_name="Flüchtlingszahl",
    new_label_name="Flucht - Flüchtlingszahl",
)
# Integration
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Bevölkerung",
    new_group_name="Soziale Hilfe",
    old_label_name="Integration",
    new_label_name="Flucht - Integration",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Bevölkerung",
    new_group_name="Soziale Hilfe",
    old_label_name="Integration",
    new_label_name="Flucht - Integration",
)
# finanzielle Unterstützung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Soziale Hilfen",
    new_group_name="Soziale Hilfe",
    old_label_name="Wohngeld",
    new_label_name="Finanzielle Unterstützung - Wohngeld",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Soziale Hilfen",
    new_group_name="Soziale Hilfe",
    old_label_name="Wohngeld",
    new_label_name="Finanzielle Unterstützung - Wohngeld",
)
# Angebot und Beratungsstelle
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Soziale Hilfen",
    new_group_name="Soziale Hilfe",
    old_label_name="Einrichtung",
    new_label_name="Angebot und Beratungsstelle",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Soziale Hilfen",
    new_group_name="Soziale Hilfe",
    old_label_name="Einrichtung",
    new_label_name="Angebot und Beratungsstelle",
)

# merge in Drogenhilfe
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Gesundheit",
    new_group_name="Soziale Hilfe",
    old_label_name="Drogenhilfe",
    new_label_name="Angebot und Beratungsstelle",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Gesundheit",
    new_group_name="Soziale Hilfe",
    old_label_name="Drogenhilfe",
    new_label_name="Angebot und Beratungsstelle",
)

# merge in Pflege and Pflegeeinrichtung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Gesundheit",
    new_group_name="Soziale Hilfe",
    old_label_name="Pflege",
    new_label_name="Pflege",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Gesundheit",
    new_group_name="Soziale Hilfe",
    old_label_name="Pflege",
    new_label_name="Pflege",
)
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Gesundheit",
    new_group_name="Soziale Hilfe",
    old_label_name="Pflegeeinrichtung",
    new_label_name="Pflege",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Gesundheit",
    new_group_name="Soziale Hilfe",
    old_label_name="Pflegeeinrichtung",
    new_label_name="Pflege",
)

# adding new ones
taxonomy = taxonomy_add_concept(
    taxonomy,
    new_group_name="Soziale Hilfe",
    new_label_name="Finanzielle Unterstützung - Grundsicherung",
)

taxonomy = taxonomy_add_concept(
    taxonomy,
    new_group_name="Soziale Hilfe",
    new_label_name="Finanzielle Unterstützung - Förderung",
)
# deleting not merged concepts
# Aufwendung
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Soziale Hilfen",
    old_label_name="Aufwendung",
    node_type="all",
)

data = data_delete_concept(
    data, old_group_name="Soziale Hilfen", old_label_name="Aufwendung", node_type="all"
)
# Ausbildung
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Soziale Hilfen",
    old_label_name="Ausbildung",
    node_type="all",
)

data = data_delete_concept(
    data, old_group_name="Soziale Hilfen", old_label_name="Ausbildung", node_type="all"
)
# Leistungsbezieher
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Soziale Hilfen",
    old_label_name="Leistungsbezieher",
    node_type="all",
)

data = data_delete_concept(
    data,
    old_group_name="Soziale Hilfen",
    old_label_name="Leistungsbezieher",
    node_type="all",
)
# Straße
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Soziale Hilfen", old_label_name="Straße", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Soziale Hilfen", old_label_name="Straße", node_type="all"
)


# Bericht
taxonomy = taxonomy_add_concept(
    taxonomy,
    new_group_name="Soziale Hilfe",
    new_label_name="Bericht",
)

#####
# Personal
#####

# rename Personal -> städtisches Personal
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Personal",
    new_group_name="Städtisches Personal",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)

data = data_rename_concept(
    data,
    old_group_name="Personal",
    new_group_name="Städtisches Personal",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)


######
# Bevölkerung
######

# rename Bevölkerung -> Bevölkerungsstruktur
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Bevölkerung",
    new_group_name="Bevölkerungsstruktur",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)

data = data_rename_concept(
    data,
    old_group_name="Bevölkerung",
    new_group_name="Bevölkerungsstruktur",
    old_label_name=None,
    new_label_name=None,
    node_type="group",
)
# rename Demografie -> Demografiebericht
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Bevölkerungsstruktur",
    new_group_name="Bevölkerungsstruktur",
    old_label_name="Demografie",
    new_label_name="Demografiebericht",
    node_type="all",
)


data = data_move_concept(
    data,
    old_group_name="Bevölkerungsstruktur",
    new_group_name="Bevölkerungsstruktur",
    old_label_name="Demografie",
    new_label_name="Demografiebericht",
)

# merge in Geburt und Sterbefall
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Bevölkerungsstruktur",
    new_group_name="Bevölkerungsstruktur",
    old_label_name="Geburt und Sterbefall",
    new_label_name="Demografiebericht",
    node_type="all",
)


data = data_move_concept(
    data,
    old_group_name="Bevölkerungsstruktur",
    new_group_name="Bevölkerungsstruktur",
    old_label_name="Geburt und Sterbefall",
    new_label_name="Demografiebericht",
)


# rename Bedargsgemeinschaft -> Haushaltszusammensetzung
taxonomy = taxonomy_add_concept(
    taxonomy,
    new_group_name="Bevölkerungsstruktur",
    new_label_name="Haushaltszusammensetzung",
)

taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Bevölkerungsstruktur",
    new_group_name="Bevölkerungsstruktur",
    old_label_name="Bedarfsgemeinschaft",
    new_label_name="Haushaltszusammensetzung",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Bevölkerungsstruktur",
    new_group_name="Bevölkerungsstruktur",
    old_label_name="Bedarfsgemeinschaft",
    new_label_name="Haushaltszusammensetzung",
)

# delete not merged or renamed ones
# Arbeit
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Bevölkerungsstruktur",
    old_label_name="Arbeit",
    node_type="all",
)

data = data_delete_concept(
    data,
    old_group_name="Bevölkerungsstruktur",
    old_label_name="Arbeit",
    node_type="all",
)
# Wohnen
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Bevölkerungsstruktur",
    old_label_name="Wohnen",
    node_type="all",
)

data = data_delete_concept(
    data,
    old_group_name="Bevölkerungsstruktur",
    old_label_name="Wohnen",
    node_type="all",
)


#####
# merge Stadtwerke in others
#####

# delete labels with few data
# Verkauf
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Stadtwerke", old_label_name="Verkauf", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Stadtwerke", old_label_name="Verkauf", node_type="all"
)

# Immobilienangebot
taxonomy = taxonomy_delete_concept(
    taxonomy,
    old_group_name="Stadtwerke",
    old_label_name="Immobilienangebot",
    node_type="all",
)

data = data_delete_concept(
    data,
    old_group_name="Stadtwerke",
    old_label_name="Immobilienangebot",
    node_type="all",
)
# Information
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Stadtwerke", old_label_name="Information", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Stadtwerke", old_label_name="Information", node_type="all"
)
# Kennzahl
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Stadtwerke", old_label_name="Kennzahl", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Stadtwerke", old_label_name="Kennzahl", node_type="all"
)

# move into Wirtschaft
# Ausschreibung und Vergabe
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Stadtwerke",
    new_group_name="Wirtschaft",
    old_label_name="Ausschreibung Vergabe",
    new_label_name="Beteiligung an Öffentlicher Wirtschaft - Ausschreibung und Vergabe",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Stadtwerke",
    new_group_name="Wirtschaft",
    old_label_name="Ausschreibung Vergabe",
    new_label_name="Wirtschaft - Ausschreibung und Vergabe",
)

# Beteiligung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Stadtwerke",
    new_group_name="Wirtschaft",
    old_label_name="Beteiligung",
    new_label_name="Beteiligung an Öffentlicher Wirtschaft - Beteiligung",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Stadtwerke",
    new_group_name="Wirtschaft",
    old_label_name="Beteiligung",
    new_label_name="Wirtschaft - Beteiligung",
)


#####
# Wohnen
#####

# merge Wohnen into other groups

# Flüchtlingsunterbringung
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wohnen",
    new_group_name="Soziale Hilfe",
    old_label_name="Flüchtlingsunterbringung",
    new_label_name="Flucht - Flüchtlingsunterbringung",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Wohnen",
    new_group_name="Soziale Hilfe",
    old_label_name="Flüchtlingsunterbringung",
    new_label_name="Flucht - Flüchtlingsunterbringung",
)

# Studentenwohnheim
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wohnen",
    new_group_name="Bildung",
    old_label_name="Studentenwohnheim",
    new_label_name="Hochschule - Studentenwohnheim",
    node_type="all",
)

data = data_move_concept(
    data,
    old_group_name="Wohnen",
    new_group_name="Bildung",
    old_label_name="Studentenwohnheim",
    new_label_name="Hochschule - Studentenwohnheim",
)

# Bauprojekt
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wohnen",
    new_group_name="Bau",
    old_label_name="Bauprojekt",
    new_label_name="Bauprojekt",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wohnen",
    new_group_name="Bau",
    old_label_name="Bauprojekt",
    new_label_name="Bauprojekt",
)
# geförderter Wohnbau
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wohnen",
    new_group_name="Soziale Hilfe",
    old_label_name="geförderter Wohnbau",
    new_label_name="Geförderter Wohnbau",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wohnen",
    new_group_name="Soziale Hilfe",
    old_label_name="geförderter Wohnbau",
    new_label_name="Geförderter Wohnbau",
)


# merge Wohnen into Bau
# Wohnungseigentum
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wohnen",
    new_group_name="Bau",
    old_label_name="Wohnungseigentum",
    new_label_name="Wohnungsbestand",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wohnen",
    new_group_name="Bau",
    old_label_name="Wohnungseigentum",
    new_label_name="Wohnungsbestand",
)
# Wohnplatz
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wohnen",
    new_group_name="Bau",
    old_label_name="Wohnplatz",
    new_label_name="Wohnungsbestand",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wohnen",
    new_group_name="Bau",
    old_label_name="Wohnplatz",
    new_label_name="Wohnungsbestand",
)
# Wohnquartier
taxonomy = taxonomy_rename_concept(
    taxonomy,
    old_group_name="Wohnen",
    new_group_name="Bau",
    old_label_name="Wohnquartier",
    new_label_name="Wohnungsbestand",
    node_type="all",
)
data = data_move_concept(
    data,
    old_group_name="Wohnen",
    new_group_name="Bau",
    old_label_name="Wohnquartier",
    new_label_name="Wohnungsbestand",
)

# delete not merged or renamed ones
# Information
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Wohnen", old_label_name="Information", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Wohnen", old_label_name="Information", node_type="all"
)
# Flächengröße
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Wohnen", old_label_name="Flächengröße", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Wohnen", old_label_name="Flächengröße", node_type="all"
)
# Sozialraum
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Wohnen", old_label_name="Sozialraum", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Wohnen", old_label_name="Sozialraum", node_type="all"
)

#####
# CLEANING
#####

# deleting anything that was not merged or renamed

# Behörden - Einrichtung
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Behörden", old_label_name="Einrichtung", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Behörden", old_label_name="Einrichtung", node_type="all"
)

# Fuhrpark - KFZ Bestand
taxonomy = taxonomy_delete_concept(
    taxonomy, old_group_name="Fuhrpark", old_label_name="KFZ Bestand", node_type="all"
)

data = data_delete_concept(
    data, old_group_name="Fuhrpark", old_label_name="KFZ Bestand", node_type="all"
)


######
# Remove Duplicates
######

taxonomy_v2 = [dict(t) for t in {tuple(d.items()) for d in taxonomy}]

######
# Data and Taxonomy Export
######

# save new taxonomy and data
# as json
save_json(obj=taxonomy_v2, path=str(settings.TAXONOMY_PROCESSED_V2))

# formatting for annotation round (concatenating title and description)
data["dct:description"] = data["dct:description"].fillna("None")
data["MUSTERDATENSATZ"] = data["MUSTERDATENSATZ"].fillna("None")
data["text"] = data[["dct:title", "dct:description"]].agg(
    " STOP TITLE START DESCRIPTION ".join, axis=1
)
data["text"] = data[["text", "MUSTERDATENSATZ"]].agg(
    " STOP DESCRIPTION START MUSTERDATENSATZ ".join, axis=1
)

data.to_csv(str(settings.BASELINE_MDK_TRAINING_DATA_PROCESSED_V2), index=False)


######
# TAXONOMY VERSION 3 - last changes and typos
######

mapper_v3_v4_data = pd.read_excel(
    f"{settings.BASE_PATH_ANNOTATIONS}/mapper/2023_02_21_v3_v4_mapper.xlsx"
)

for old, new in zip(mapper_v3_v4_data.old, mapper_v3_v4_data.new):
    taxonomy = taxonomy_rename_or_delete_concept(
        taxonomy=taxonomy,
        old_group_name=old.split("-", 1)[0].rstrip(),
        new_group_name=new.split("-", 1)[0].rstrip(),
        old_label_name=old.split("-", 1)[1].lstrip(),
        new_label_name=new.split("-", 1)[1].lstrip(),
    )

taxonomy_v3 = [dict(t) for t in {tuple(d.items()) for d in taxonomy}]
save_json(obj=taxonomy_v3, path=str(settings.TAXONOMY_PROCESSED_V3))

# generating log file
generate_excel_log()

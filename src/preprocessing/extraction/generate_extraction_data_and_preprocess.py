from datetime import date

import pandas as pd

df = pd.read_excel("extraction/musterdatenkatalog/musterdatenkatalog.xlsx")

df = df.rename(
    columns={
        "url": "dcat:landingpage",
        "city": "ORG",
        "license": "dcat:Distribution.dct:license",
        "tags": "dcat:theme",
        "thema": "THEMA",
        "bezeichnung": "BEZEICHNUNG",
    }
)

df["MUSTERDATENSATZ"] = df["THEMA"] + " - " + df["BEZEICHNUNG"]

df_small = df[
    [
        "dct:title",
        "dct:identifier",
        "dcat:landingpage",
        "dct:description",
        "ORG",
        "dcat:Distribution.dct:license",
        "dcat:theme",
        "updated_at",
        "added",
        "MUSTERDATENSATZ",
        "THEMA",
        "BEZEICHNUNG",
    ]
]

df.to_excel(f"extraction/musterdatenkatalog/{date.today()}_musterdatenkatalog_all.xlsx")
df.to_csv(f"extraction/musterdatenkatalog/{date.today()}_musterdatenkatalog_all.csv")

df_small.to_excel(
    f"extraction/musterdatenkatalog/{date.today()}_musterdatenkatalog.xlsx"
)
df_small.to_csv(f"extraction/musterdatenkatalog/{date.today()}_musterdatenkatalog.csv")

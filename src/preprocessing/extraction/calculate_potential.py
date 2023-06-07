import pandas as pd

# Read the data
df = pd.read_excel(
    "extraction/musterdatenkatalog/2023-04-20_musterdatenkatalog.xlsx"  # noqa: E501
)

org_by_md = df.groupby("ORG")["MUSTERDATENSATZ"].apply(list).to_dict()

org_by_md_unique = {org: set(md) for org, md in org_by_md.items()}

org_by_md_unique_count = {org: len(md) for org, md in org_by_md_unique.items()}

df_potential = (
    pd.DataFrame.from_dict(
        org_by_md_unique_count, orient="index", columns=["Musterdatensätze"]
    )
    .reset_index()
    .rename(columns={"index": "Stadt"})
)

df_potential.to_excel(
    "extraction/musterdatenkatalog/2023-04-20_musterdatenkatalog_potential.xlsx"  # noqa: E501
)

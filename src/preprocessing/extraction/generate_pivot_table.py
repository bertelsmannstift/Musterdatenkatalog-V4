import pandas as pd

# Read the data
df = pd.read_excel(
    "extraction/musterdatenkatalog/2023-04-20_musterdatenkatalog.xlsx"  # noqa: E501
)

df_count = df.groupby(by=["ORG", "MUSTERDATENSATZ"]).count()

df_count.reset_index()[["ORG", "MUSTERDATENSATZ", "BEZEICHNUNG"]]

# Create a pivot table
pivot_table = pd.pivot_table(
    df,
    values="BEZEICHNUNG",
    index=["MUSTERDATENSATZ"],
    columns=["ORG"],
    aggfunc="count",
)

pivot_table.to_excel(
    "extraction/musterdatenkatalog/2023-04-20_musterdatenkatalog_pivot.xlsx"  # noqa: E501
)

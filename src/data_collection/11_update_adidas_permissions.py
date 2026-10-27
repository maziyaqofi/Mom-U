import pandas as pd
from pathlib import Path

audit_path = Path("data/processed/source_permissions.csv")

df = pd.read_csv(audit_path, keep_default_na=False)

mask = (
    (df["document_id"] == "MOMU_024")
    & (df["source"] == "Adidas Blog")
)

df.loc[mask, "permission_status"] = "restricted"

df.loc[mask, "permission_reference"] = (
    "https://www.adidas.com/us/help/us-confirmed-app/"
    "confirmed-app-terms-and-conditions"
)

df.loc[mask, "usage_notes"] = (
    "Adidas terms restrict content reuse and automated collection. "
    "Verify the terms applicable to the article website. "
    "Do not extract full text without appropriate permission."
)

df.to_csv(audit_path, index=False)

print("Adidas permission record updated successfully!")
print("Updated articles:", int(mask.sum()))
print()
print(df["permission_status"].value_counts().to_string())
import pandas as pd
from pathlib import Path

# Define audit file
audit_path = Path("data/processed/source_permissions.csv")

# Load permission audit
df = pd.read_csv(audit_path, keep_default_na=False)

# Define permission information
permission_reference = (
    "https://medlineplus.gov/about/using/usingcontent/"
)

usage_notes = (
    "Public domain: MedlinePlus Health Topic Summary only. "
    "Exclude third-party links, copyrighted encyclopedia "
    "content, images, and licensed materials. "
    "Attribution required by MedlinePlus guidance."
)

# Select the verified MedlinePlus records
document_ids = ["MOMU_012", "MOMU_021"]

mask = (
    (df["source"] == "MedlinePlus")
    & df["document_id"].isin(document_ids)
)

# Update permission records
df.loc[mask, "permission_status"] = "allowed"
df.loc[mask, "permission_reference"] = permission_reference
df.loc[mask, "usage_notes"] = usage_notes

# Save updated audit
df.to_csv(audit_path, index=False)

print("MedlinePlus permission records updated successfully!")
print("Updated articles:", int(mask.sum()))
print("Total articles:", len(df))
print()
print(df["permission_status"].value_counts().to_string())
import pandas as pd
from pathlib import Path

# Define audit file
audit_path = Path("data/processed/source_permissions.csv")

# Load permission audit
df = pd.read_csv(audit_path, keep_default_na=False)

# Define Mayo Clinic permission information
permission_reference = (
    "https://www.mayoclinic.org/about-this-site/"
    "terms-conditions-use-policy"
)

usage_notes = (
    "Copyright-protected content. General terms restrict copying "
    "and prohibit automated scraping or crawling. "
    "Full-text corpus extraction and electronic redistribution "
    "require prior written authorization."
)

# Select Mayo Clinic records
document_ids = ["MOMU_020", "MOMU_022", "MOMU_028"]

mask = (
    (df["source"] == "Mayo Clinic")
    & df["document_id"].isin(document_ids)
)

# Update permission records
df.loc[mask, "permission_status"] = "restricted"
df.loc[mask, "permission_reference"] = permission_reference
df.loc[mask, "usage_notes"] = usage_notes

# Save updated audit
df.to_csv(audit_path, index=False)

print("Mayo Clinic permission records updated successfully!")
print("Updated articles:", int(mask.sum()))
print("Total articles:", len(df))
print()
print(df["permission_status"].value_counts().to_string())
import pandas as pd
from pathlib import Path

# Define audit file
audit_path = Path("data/processed/source_permissions.csv")

# Load permission audit
df = pd.read_csv(audit_path, keep_default_na=False)

# Select WHO article
mask = df["document_id"] == "MOMU_019"

# Update permission information
df.loc[mask, "permission_status"] = "restricted"

df.loc[mask, "permission_reference"] = (
    "https://www.who.int/about/policies/terms-of-use"
)

df.loc[mask, "usage_notes"] = (
    "WHO website terms permit excerpts for research or private "
    "study with attribution and non-commercial use. "
    "Substantial reproduction requires prior written permission. "
    "Do not include full page text in a public corpus."
)

# Save updated audit
df.to_csv(audit_path, index=False)

print("WHO permission record updated successfully!")
print("Updated articles:", int(mask.sum()))
print("Total articles:", len(df))
print()
print(df["permission_status"].value_counts().to_string())
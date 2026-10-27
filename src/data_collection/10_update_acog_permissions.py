import pandas as pd
from pathlib import Path

# Define audit file
audit_path = Path("data/processed/source_permissions.csv")

# Load permission audit
df = pd.read_csv(audit_path, keep_default_na=False)

# Define ACOG permission information
permission_reference = (
    "https://www.acog.org/legal/terms-of-use"
)

usage_notes = (
    "Copyright-protected content. ACOG terms prohibit "
    "unauthorized copying, automated scraping, and incorporation "
    "into information retrieval systems. "
    "Prior written permission is required for the planned use."
)

# Select ACOG records
document_ids = ["MOMU_018", "MOMU_025"]

mask = (
    (df["source"] == "ACOG")
    & df["document_id"].isin(document_ids)
)

# Update permission records
df.loc[mask, "permission_status"] = "restricted"
df.loc[mask, "permission_reference"] = permission_reference
df.loc[mask, "usage_notes"] = usage_notes

# Save updated audit
df.to_csv(audit_path, index=False)

print("ACOG permission records updated successfully!")
print("Updated articles:", int(mask.sum()))
print("Total articles:", len(df))
print()
print(df["permission_status"].value_counts().to_string())
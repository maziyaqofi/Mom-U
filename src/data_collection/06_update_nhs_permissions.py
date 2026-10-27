import pandas as pd
from pathlib import Path

# Define audit file
audit_path = Path("data/processed/source_permissions.csv")

# Load permission audit
df = pd.read_csv(audit_path, keep_default_na=False)

# Define NHS permission information
nhs_reference = "https://www.nhs.uk/our-policies/terms-and-conditions/"

nhs_notes = (
    "OGL v3.0; text reuse subject to NHS terms, attribution, "
    "content freshness, and third-party exclusions. "
    "Verify page-specific exclusions before extraction."
)

# Update NHS records
nhs_mask = df["source"] == "NHS"

df.loc[nhs_mask, "permission_status"] = "allowed"
df.loc[nhs_mask, "permission_reference"] = nhs_reference
df.loc[nhs_mask, "usage_notes"] = nhs_notes

# Save updated audit
df.to_csv(audit_path, index=False)

print("NHS permission records updated successfully!")
print("Updated NHS articles:", int(nhs_mask.sum()))
print("Total articles:", len(df))
print()
print(df["permission_status"].value_counts().to_string())
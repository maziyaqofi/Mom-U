import csv
from pathlib import Path

# Define file paths
audit_path = Path("data/processed/source_permissions.csv")

# Define verified permission updates
permission_updates = {
    # Add verified records here.
    # Example:
    # "MOMU_005": {
    #     "permission_status": "allowed",
    #     "permission_reference": "https://example.org/license",
    #     "usage_notes": "Reuse permitted under the stated license."
    # }
}

# Load existing permission records
with open(audit_path, "r", encoding="utf-8", newline="") as file:
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames
    records = list(reader)

if not fieldnames:
    raise ValueError("Permission audit file has no header.")

# Apply verified updates
updated_count = 0

for record in records:
    document_id = record["document_id"]

    if document_id in permission_updates:
        update = permission_updates[document_id]

        for field, value in update.items():
            if field not in fieldnames:
                raise ValueError(f"Unknown field: {field}")

            record[field] = value

        updated_count += 1

# Save updated records
with open(audit_path, "w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(records)

# Display audit summary
status_counts = {}

for record in records:
    status = record["permission_status"]
    status_counts[status] = status_counts.get(status, 0) + 1

print("Permission audit manager completed!")
print("Updated records:", updated_count)
print("Total articles:", len(records))

for status, count in sorted(status_counts.items()):
    print(f"{status}: {count}")
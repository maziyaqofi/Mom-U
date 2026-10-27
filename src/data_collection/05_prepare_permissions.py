import json
import csv
from pathlib import Path

# Define input and output paths
input_path = Path("data/processed/corpus_inventory.jsonl")
output_path = Path("data/processed/source_permissions.csv")

# Load corpus inventory
documents = []

with open(input_path, "r", encoding="utf-8") as file:
    for line in file:
        if line.strip():
            documents.append(json.loads(line))

# Prepare permission audit records
records = []

for document in documents:
    record = {
        "document_id": document["document_id"],
        "source": document["source"],
        "url": document["url"],
        "permission_status": "not_verified",
        "permission_reference": "",
        "usage_notes": ""
    }

    records.append(record)

# Save permission audit file
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "document_id",
            "source",
            "url",
            "permission_status",
            "permission_reference",
            "usage_notes"
        ]
    )

    writer.writeheader()
    writer.writerows(records)

print("Source permission audit created successfully!")
print("Total articles:", len(records))
print("Output file:", output_path)
import json
import pandas as pd
from pathlib import Path

# Define file paths
inventory_path = Path("data/processed/corpus_inventory.jsonl")
permissions_path = Path("data/processed/source_permissions.csv")
output_path = Path("data/processed/extraction_policy.jsonl")

# Load corpus inventory
documents = []

with open(inventory_path, "r", encoding="utf-8") as file:
    for line in file:
        if line.strip():
            documents.append(json.loads(line))

# Load permission audit
permissions = pd.read_csv(
    permissions_path,
    keep_default_na=False
)

# Build permission lookup
permission_lookup = permissions.set_index(
    "document_id"
).to_dict("index")

# Define source-specific extraction rules
extraction_rules = {
    "NHS": "full_article_text",
    "MedlinePlus": "health_topic_summary"
}

# Prepare extraction policy
policies = []

for document in documents:
    document_id = document["document_id"]

    permission = permission_lookup.get(document_id, {})

    status = permission.get(
        "permission_status",
        "not_verified"
    )

    source = document["source"]

    if status == "allowed":
        extraction_scope = extraction_rules.get(
            source,
            "metadata_only"
        )
    else:
        extraction_scope = "metadata_only"

    policy = {
        "document_id": document_id,
        "source": source,
        "url": document["url"],
        "permission_status": status,
        "extraction_scope": extraction_scope,
        "permission_reference": permission.get(
            "permission_reference",
            ""
        ),
        "usage_notes": permission.get(
            "usage_notes",
            ""
        )
    }

    policies.append(policy)

# Save extraction policy
output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

with open(output_path, "w", encoding="utf-8") as file:
    for policy in policies:
        file.write(
            json.dumps(policy, ensure_ascii=False) + "\n"
        )

# Display summary
scope_counts = {}

for policy in policies:
    scope = policy["extraction_scope"]
    scope_counts[scope] = scope_counts.get(scope, 0) + 1

print("Extraction policy created successfully!")
print("Total documents:", len(policies))

for scope, count in sorted(scope_counts.items()):
    print(f"{scope}: {count}")

print("Output file:", output_path)
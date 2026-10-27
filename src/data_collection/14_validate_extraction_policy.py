import json
from collections import Counter
from pathlib import Path

# Define input path
input_path = Path("data/processed/extraction_policy.jsonl")

# Define valid extraction scopes
valid_scopes = {
    "full_article_text",
    "health_topic_summary",
    "metadata_only"
}

# Load extraction policies
policies = []

with open(input_path, "r", encoding="utf-8") as file:
    for line_number, line in enumerate(file, start=1):
        if not line.strip():
            continue

        policy = json.loads(line)
        policies.append(policy)

# Validate document count
assert len(policies) == 30, "Expected 30 documents."

# Validate unique document IDs
document_ids = [policy["document_id"] for policy in policies]

assert len(document_ids) == len(set(document_ids)), (
    "Duplicate document IDs detected."
)

# Validate permission and extraction consistency
for policy in policies:
    document_id = policy["document_id"]
    source = policy["source"]
    status = policy["permission_status"]
    scope = policy["extraction_scope"]

    assert scope in valid_scopes, (
        f"Invalid extraction scope: {document_id}"
    )

    if status != "allowed":
        assert scope == "metadata_only", (
            f"Unauthorized extraction scope: {document_id}"
        )

    if scope == "full_article_text":
        assert source == "NHS", (
            f"Unexpected full-text source: {document_id}"
        )

    if scope == "health_topic_summary":
        assert source == "MedlinePlus", (
            f"Unexpected summary source: {document_id}"
        )

# Display validation results
scope_counts = Counter(
    policy["extraction_scope"] for policy in policies
)

print("Extraction policy validation passed!")
print("Total documents:", len(policies))
print("Unique document IDs:", len(set(document_ids)))

for scope, count in sorted(scope_counts.items()):
    print(f"{scope}: {count}")
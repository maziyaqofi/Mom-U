import json
from pathlib import Path
from collections import Counter

# Define file paths
inventory_path = Path("data/processed/corpus_inventory.jsonl")
policy_path = Path("data/processed/extraction_policy.jsonl")
output_path = Path("data/processed/pregnancy_corpus.jsonl")

# Load JSONL records
def load_jsonl(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records


# Load inventory and extraction policy
inventory = load_jsonl(inventory_path)
policies = load_jsonl(policy_path)

# Build policy lookup
policy_lookup = {
    policy["document_id"]: policy
    for policy in policies
}

# Prepare corpus records
corpus = []

for document in inventory:
    document_id = document["document_id"]
    policy = policy_lookup.get(document_id)

    if policy is None:
        raise ValueError(
            f"Missing extraction policy for {document_id}"
        )

    scope = policy["extraction_scope"]

    # Do not perform network extraction at this stage
    if scope == "metadata_only":
        status = "metadata_only"
    else:
        status = "pending_extraction"

    record = {
        "document_id": document_id,
        "title": document["title"],
        "category": document["category"],
        "source": document["source"],
        "url": document["url"],
        "language": "en",
        "content": None,
        "extraction_scope": scope,
        "extraction_status": status
    }

    corpus.append(record)

# Save corpus
output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

with open(output_path, "w", encoding="utf-8") as file:
    for record in corpus:
        file.write(
            json.dumps(record, ensure_ascii=False) + "\n"
        )

# Display summary
status_counts = Counter(
    record["extraction_status"]
    for record in corpus
)

print("Corpus extraction pipeline initialized!")
print("Total documents:", len(corpus))

for status, count in sorted(status_counts.items()):
    print(f"{status}: {count}")

print("Output file:", output_path)
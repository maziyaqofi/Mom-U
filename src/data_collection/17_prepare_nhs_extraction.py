import json
from pathlib import Path

# Define file paths
policy_path = Path("data/processed/extraction_policy.jsonl")

# Load extraction policies
policies = []

with open(policy_path, "r", encoding="utf-8") as file:
    for line in file:
        if line.strip():
            policies.append(json.loads(line))

# Select NHS articles
nhs_documents = [
    policy
    for policy in policies
    if policy["source"] == "NHS"
    and policy["permission_status"] == "allowed"
    and policy["extraction_scope"] == "full_article_text"
]

# Display extraction plan
print("NHS extraction preparation completed!")
print("Total NHS documents:", len(nhs_documents))
print()

for document in nhs_documents:
    print("Document ID:", document["document_id"])
    print("URL:", document["url"])
    print("Extraction scope:", document["extraction_scope"])
    print("-" * 50)

print("Dry run completed. No network requests were made.")
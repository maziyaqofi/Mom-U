import json
from pathlib import Path

# Define file paths
sample_path = Path("data/processed/sample_corpus.jsonl")
corpus_path = Path("data/processed/pregnancy_corpus.jsonl")

# Load JSONL records
def load_jsonl(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records


# Load sample and corpus
samples = load_jsonl(sample_path)
corpus = load_jsonl(corpus_path)

# Build corpus lookup
corpus_lookup = {
    document["document_id"]: document
    for document in corpus
}

# Validate sample extraction
for sample in samples:
    document_id = sample["document_id"]

    if document_id not in corpus_lookup:
        raise ValueError(
            f"Document not found in corpus: {document_id}"
        )

    document = corpus_lookup[document_id]

    if document["url"] != sample["url"]:
        raise ValueError(
            f"URL mismatch for {document_id}"
        )

    if not sample.get("content"):
        raise ValueError(
            f"Empty sample content: {document_id}"
        )

    print("Document ID:", document_id)
    print("Source:", document["source"])
    print("Extraction scope:", document["extraction_scope"])
    print("Sample content length:", len(sample["content"]))
    print("Sample validation passed!")

print("All sample documents validated successfully!")
import json
from pathlib import Path

# Define the corpus file path
file_path = Path("data/processed/sample_corpus.jsonl")

# Define required document fields
required_fields = [
    "document_id",
    "title",
    "category",
    "source",
    "url",
    "content"
]

# Load and validate the corpus
with open(file_path, "r", encoding="utf-8") as file:
    for line_number, line in enumerate(file, start=1):
        document = json.loads(line)

        # Check required fields
        missing_fields = [
            field for field in required_fields
            if not document.get(field)
        ]

        print("Document ID:", document.get("document_id"))
        print("Title:", document.get("title"))
        print("Source:", document.get("source"))
        print("Content length:", len(document.get("content", "")))

        if missing_fields:
            print("Validation failed:", missing_fields)
        else:
            print("Validation passed!")

        print("-" * 40)
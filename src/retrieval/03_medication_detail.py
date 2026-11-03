
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CORPUS_PATH = (
    PROJECT_ROOT
    / "data/processed/medication_corpus.jsonl"
)

SOURCE_URL = (
    "https://www.tga.gov.au/resources/"
    "health-professional-information-and-resources/"
    "australian-categorisation-system-prescribing-medicines-pregnancy/"
    "prescribing-medicines-pregnancy-database"
)


def load_documents():
    """Load medication documents indexed by document ID."""
    documents = {}

    with CORPUS_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            document = json.loads(line)
            documents[document["document_id"]] = document

    return documents


def display_medication(document):
    """Display the original TGA medication information."""
    print("\n=== Medication Information ===")
    print(f"Document ID: {document['document_id']}")
    print(f"Medication: {document['Name']}")
    print(f"Pregnancy Category: {document['Category']}")

    for level in range(1, 4):
        field = f"Classification {level}"
        value = document.get(field, "")

        if value:
            print(f"{field}: {value}")

    statement = document.get("Safety statement", "")

    print("\nSafety Statement:")
    print(statement if statement else "Not available in this dataset.")

    print("\nSource: Australian Therapeutic Goods Administration")
    print(f"Source URL: {SOURCE_URL}")

    print(
        "\nDisclaimer: Pregnancy categories are not an "
        "ordinal safety scale. This record is informational "
        "and does not replace professional medical advice."
    )


def main():
    documents = load_documents()

    print(f"Loaded {len(documents)} medication documents.")

    while True:
        document_id = input(
            "\nEnter confirmed document ID (or 'exit'): "
        ).strip().upper()

        if document_id == "EXIT":
            break

        document = documents.get(document_id)

        if document is None:
            print("Document ID not found.")
            continue

        display_medication(document)


if __name__ == "__main__":
    main()


import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CORPUS_PATH = (
    PROJECT_ROOT / "data/processed/medication_corpus.jsonl"
)

OUTPUT_DIR = PROJECT_ROOT / "data/evaluation"


MEDICATIONS = [
    ("paracetamol", "TGA_01250"),
    ("ibuprofen", "TGA_00831"),
    ("aspirin", "TGA_00129"),
    ("amoxicillin", "TGA_00090"),
    ("metformin", "TGA_01052"),
    ("folic acid", "TGA_00719"),
    ("omeprazole", "TGA_01205"),
    ("cetirizine", "TGA_00315"),
    ("loratadine", "TGA_01000"),
    ("ondansetron", "TGA_01207"),
    ("naproxen", "TGA_01133"),
    ("ketoprofen", "TGA_00923"),
]


def load_corpus():
    """Load medication documents from the processed corpus."""
    with CORPUS_PATH.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file]


def validate_medications(documents):
    """Verify target document IDs and medication names."""
    documents_by_id = {
        document["document_id"]: document
        for document in documents
    }

    for name, document_id in MEDICATIONS:
        document = documents_by_id.get(document_id)

        if document is None:
            raise ValueError(
                f"Document not found: {document_id}"
            )

        if document["normalized_name"] != name:
            raise ValueError(
                f"Medication mismatch: {name} ({document_id})"
            )

    print(f"Validated medications: {len(MEDICATIONS)}")


def generate_queries():
    """Generate medication-specific evaluation queries."""
    queries = []
    judgments = []

    query_number = 1

    for medication, document_id in MEDICATIONS:
        query_variants = [
            (
                "exact_name",
                "en",
                medication,
            ),
            (
                "english_question",
                "en",
                f"What is the pregnancy safety information for {medication}?",
            ),
            (
                "indonesian_question",
                "id",
                f"Apakah {medication} aman untuk ibu hamil?",
            ),
        ]

        for query_type, language, query_text in query_variants:
            query_id = f"Q{query_number:03d}"

            queries.append({
                "query_id": query_id,
                "query_text": query_text,
                "query_type": query_type,
                "language": language,
                "target_medication": medication,
                "target_document_id": document_id,
            })

            judgments.append({
                "query_id": query_id,
                "document_id": document_id,
                "relevance": 2,
                "annotation_status": "seed_target",
            })

            query_number += 1

    return queries, judgments


def save_csv(path, rows, fieldnames):
    """Save records to a UTF-8 CSV file."""
    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)


def main():
    print("Loading medication corpus...")
    documents = load_corpus()

    print(f"Total documents: {len(documents)}")

    validate_medications(documents)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    queries, judgments = generate_queries()

    save_csv(
        OUTPUT_DIR / "evaluation_queries.csv",
        queries,
        [
            "query_id",
            "query_text",
            "query_type",
            "language",
            "target_medication",
            "target_document_id",
        ],
    )

    save_csv(
        OUTPUT_DIR / "relevance_judgments.csv",
        judgments,
        [
            "query_id",
            "document_id",
            "relevance",
            "annotation_status",
        ],
    )

    print(f"Evaluation queries generated: {len(queries)}")
    print(f"Seed relevance judgments generated: {len(judgments)}")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

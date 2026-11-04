
import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = (
    PROJECT_ROOT / "data/evaluation/robustness_queries.csv"
)


TEST_CASES = [
    {
        "query_id": "R001",
        "query_type": "exact_name",
        "query_text": "paracetamol",
        "expected_medications": "paracetamol",
        "expected_document_ids": "TGA_01250",
        "evaluation_scope": "single_target",
    },
    {
        "query_id": "R002",
        "query_type": "indonesian_question",
        "query_text": "Apakah ibuprofen aman untuk ibu hamil?",
        "expected_medications": "ibuprofen",
        "expected_document_ids": "TGA_00831",
        "evaluation_scope": "single_target",
    },
    {
        "query_id": "R003",
        "query_type": "english_question",
        "query_text": "Can I take loratadine during pregnancy?",
        "expected_medications": "loratadine",
        "expected_document_ids": "TGA_01000",
        "evaluation_scope": "single_target",
    },
    {
        "query_id": "R004",
        "query_type": "misspelling",
        "query_text": "loratadin",
        "expected_medications": "loratadine",
        "expected_document_ids": "TGA_01000",
        "evaluation_scope": "single_target",
    },
    {
        "query_id": "R005",
        "query_type": "misspelling",
        "query_text": "paracetmol",
        "expected_medications": "paracetamol",
        "expected_document_ids": "TGA_01250",
        "evaluation_scope": "single_target",
    },
    {
        "query_id": "R006",
        "query_type": "brand_name",
        "query_text": "Panadol",
        "expected_medications": "paracetamol",
        "expected_document_ids": "TGA_01250",
        "evaluation_scope": "single_target",
    },
    {
        "query_id": "R007",
        "query_type": "combination_medication",
        "query_text": "Is aspirin / dipyridamole safe during pregnancy?",
        "expected_medications": "aspirin / dipyridamole",
        "expected_document_ids": "TGA_00130",
        "evaluation_scope": "single_target",
    },
    {
        "query_id": "R008",
        "query_type": "multi_medication",
        "query_text": "Can I take paracetamol and ibuprofen during pregnancy?",
        "expected_medications": "paracetamol|ibuprofen",
        "expected_document_ids": "TGA_01250|TGA_00831",
        "evaluation_scope": "multi_target",
    },
    {
        "query_id": "R009",
        "query_type": "ocr_like",
        "query_text": "PARACETAMOL 500 MG TABLETS",
        "expected_medications": "paracetamol",
        "expected_document_ids": "TGA_01250",
        "evaluation_scope": "single_target",
    },
    {
        "query_id": "R010",
        "query_type": "ocr_like",
        "query_text": "IBUPROFEN 200MG FILM COATED TABLETS",
        "expected_medications": "ibuprofen",
        "expected_document_ids": "TGA_00831",
        "evaluation_scope": "single_target",
    },
    {
        "query_id": "R011",
        "query_type": "ocr_like_typo",
        "query_text": "PARACETAM0L 500 MG",
        "expected_medications": "paracetamol",
        "expected_document_ids": "TGA_01250",
        "evaluation_scope": "single_target",
    },
    {
        "query_id": "R012",
        "query_type": "general_question",
        "query_text": "What medications are used for pain relief during pregnancy?",
        "expected_medications": "",
        "expected_document_ids": "",
        "evaluation_scope": "exploratory",
    },
    {
        "query_id": "R013",
        "query_type": "general_question",
        "query_text": "Obat apa yang boleh digunakan saat hamil?",
        "expected_medications": "",
        "expected_document_ids": "",
        "evaluation_scope": "exploratory",
    },
    {
        "query_id": "R014",
        "query_type": "unknown_medication",
        "query_text": "xyzmedication123",
        "expected_medications": "",
        "expected_document_ids": "",
        "evaluation_scope": "no_known_target",
    },
]


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "query_id",
        "query_type",
        "query_text",
        "expected_medications",
        "expected_document_ids",
        "evaluation_scope",
    ]

    with OUTPUT_PATH.open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(TEST_CASES)

    print("=== Robustness Dataset Preparation ===")
    print(f"Total queries: {len(TEST_CASES)}")
    print(f"Output: {OUTPUT_PATH}")

    print("\nQuery distribution:")
    query_types = sorted(
        set(item["query_type"] for item in TEST_CASES)
    )

    for query_type in query_types:
        count = sum(
            item["query_type"] == query_type
            for item in TEST_CASES
        )
        print(f"{query_type}: {count}")


if __name__ == "__main__":
    main()

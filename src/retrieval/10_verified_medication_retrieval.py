
import importlib.util
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RETRIEVAL_DIR = PROJECT_ROOT / "src/retrieval"
CORPUS_PATH = (
    PROJECT_ROOT / "data/processed/medication_corpus.jsonl"
)


def load_module(filename, module_name):
    """Load an existing retrieval module."""
    path = RETRIEVAL_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_document_index():
    """Load TGA medication documents indexed by document ID."""
    documents = {}

    with CORPUS_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            document = json.loads(line)
            document_id = document["document_id"]

            if document_id in documents:
                raise ValueError(
                    f"Duplicate document ID: {document_id}"
                )

            documents[document_id] = document

    return documents


def clean_value(value):
    """Convert missing or empty fields to None."""
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()

        if value.lower() in {"", "nan", "none", "null"}:
            return None

    return value


def retrieve_verified_medications(
    verification,
    document_index,
):
    """Retrieve TGA records for user-confirmed medication IDs."""
    if verification.get("status") != "user_confirmed":
        raise ValueError(
            "Medication identity must be user-confirmed "
            "before verified retrieval."
        )

    selected_medications = verification.get(
        "selected_medications", []
    )

    if not selected_medications:
        raise ValueError("No confirmed medications found.")

    results = []

    for selected in selected_medications:
        document_id = selected["document_id"]

        if document_id not in document_index:
            raise KeyError(
                f"TGA document not found: {document_id}"
            )

        document = document_index[document_id]

        confirmed_name = selected["name"]
        corpus_name = document.get("Name")

        if confirmed_name.casefold() != corpus_name.casefold():
            raise ValueError(
                f"Medication name mismatch for {document_id}"
            )

        safety_statement = clean_value(
            document.get("Safety statement")
        )

        results.append({
            "document_id": document_id,
            "medication_name": corpus_name,
            "pregnancy_category": clean_value(
                document.get("Category")
            ),
            "safety_statement": safety_statement,
            "safety_statement_available": (
                safety_statement is not None
            ),
            "classification_1": clean_value(
                document.get("Classification 1")
            ),
            "classification_2": clean_value(
                document.get("Classification 2")
            ),
            "classification_3": clean_value(
                document.get("Classification 3")
            ),
            "source": "Australian TGA Pregnancy Database",
        })

    return results


def main():
    matching = load_module(
        "02_medication_name_matching.py",
        "medication_matching",
    )
    recognition = load_module(
        "06_medication_entity_recognition.py",
        "medication_recognition",
    )
    resolver = load_module(
        "08_medication_candidate_resolution.py",
        "medication_candidate_resolution",
    )
    verification_module = load_module(
        "09_medication_identity_verification.py",
        "medication_identity_verification",
    )

    medications = matching.load_medications()
    document_index = load_document_index()

    test_queries = [
        "loratadine",
        "loratadin",
        "paracetmol",
        "Panadol",
        "Can I take paracetamol and ibuprofen during pregnancy?",
    ]

    print("=== EXP-004I Verified Medication Retrieval ===")
    print(f"Indexed TGA documents: {len(document_index)}")

    for query in test_queries:
        verification = verification_module.prepare_verification(
            query,
            resolver,
            medications,
            matching,
            recognition,
        )

        print(f"\nQuery: {query}")
        print(f"Resolution status: {verification['status']}")

        if not verification["candidates"]:
            print("Retrieval blocked: No candidate to confirm.")
            continue

        # Simulate an explicit user selection for testing only.
        # This is not automatic confirmation in the application.
        if verification["status"] == "candidate_suggested":
            selected_ids = [
                verification["candidates"][0]["document_ids"][0]
            ]
        else:
            selected_ids = [
                candidate["document_ids"][0]
                for candidate in verification["candidates"]
            ]

        confirmed = verification_module.confirm_medications(
            verification,
            selected_ids,
        )

        results = retrieve_verified_medications(
            confirmed,
            document_index,
        )

        for result in results:
            print(f"Document ID: {result['document_id']}")
            print(f"Medication: {result['medication_name']}")
            print(
                "Pregnancy category: "
                f"{result['pregnancy_category']}"
            )
            print(
                "Safety statement available: "
                f"{result['safety_statement_available']}"
            )

            if result["safety_statement_available"]:
                print(
                    f"Safety statement: "
                    f"{result['safety_statement']}"
                )
            else:
                print(
                    "Safety statement: Not available "
                    "in the current corpus."
                )

            print(f"Source: {result['source']}")


if __name__ == "__main__":
    main()

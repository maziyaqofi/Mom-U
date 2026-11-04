
import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RETRIEVAL_DIR = PROJECT_ROOT / "src/retrieval"


def load_module(filename, module_name):
    """Load an existing retrieval module."""
    path = RETRIEVAL_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare_verification(query, resolver, medications, matching, recognition):
    """Prepare medication identity candidates for verification."""
    resolution = resolver.resolve_medication(
        query,
        medications,
        matching,
        recognition,
    )

    if resolution["status"] == "matched":
        return {
            "query": query,
            "status": "name_matched",
            "candidates": resolution["entities"],
            "selected_medications": [],
            "requires_user_confirmation": True,
        }

    if resolution["status"] == "confirmation_required":
        return {
            "query": query,
            "status": "candidate_suggested",
            "candidates": resolution["suggestions"],
            "selected_medications": [],
            "requires_user_confirmation": True,
        }

    return {
        "query": query,
        "status": "unresolved",
        "candidates": [],
        "selected_medications": [],
        "requires_user_confirmation": True,
    }


def confirm_medications(verification, selected_document_ids):
    """Confirm explicitly selected candidates by document ID."""
    candidate_map = {}

    for candidate in verification["candidates"]:
        for document_id in candidate["document_ids"]:
            candidate_map[document_id] = candidate

    selected = []
    seen = set()

    for document_id in selected_document_ids:
        if document_id not in candidate_map:
            raise ValueError(
                f"Document ID is not an offered candidate: {document_id}"
            )

        if document_id in seen:
            continue

        candidate = candidate_map[document_id]

        selected.append({
            "name": candidate["name"],
            "document_id": document_id,
        })
        seen.add(document_id)

    if not selected:
        raise ValueError("At least one candidate must be selected.")

    return {
        **verification,
        "status": "user_confirmed",
        "selected_medications": selected,
        "requires_user_confirmation": False,
    }


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

    medications = matching.load_medications()

    test_queries = [
        "loratadine",
        "loratadin",
        "paracetmol",
        "Panadol",
        "PARACETAM0L 500 MG",
        "Can I take paracetamol and ibuprofen during pregnancy?",
    ]

    print("=== Medication Identity Verification Test ===")

    for query in test_queries:
        verification = prepare_verification(
            query,
            resolver,
            medications,
            matching,
            recognition,
        )

        print(f"\nQuery: {query}")
        print(f"Status: {verification['status']}")
        print(
            "Requires user confirmation: "
            f"{verification['requires_user_confirmation']}"
        )

        for candidate in verification["candidates"]:
            print(
                f"Candidate: {candidate['name']} "
                f"| Documents: {', '.join(candidate['document_ids'])}"
            )

        # This is a simulated user action for testing only.
        
        # Simulate user selection for testing purposes only.
        # Fuzzy suggestions must not be confirmed automatically.
        if verification["candidates"]:
            if verification["status"] == "candidate_suggested":
                selected_ids = [
                    verification["candidates"][0]["document_ids"][0]
                ]
                print("Test scenario: User selects the first suggestion.")

            else:
                selected_ids = [
                    candidate["document_ids"][0]
                    for candidate in verification["candidates"]
                ]
                print("Test scenario: User selects all explicit matches.")

            confirmed = confirm_medications(
                verification,
                selected_ids,
            )

            for medication in confirmed["selected_medications"]:
                print(
                    f"Simulated selection: {medication['name']}"
                )

            print(f"Final status: {confirmed['status']}")

        else:
            print("No candidate available for confirmation.")


if __name__ == "__main__":
    main()

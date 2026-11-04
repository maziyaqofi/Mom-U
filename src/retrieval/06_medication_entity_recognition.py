
import importlib.util
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MATCHING_SCRIPT = (
    PROJECT_ROOT / "src/retrieval/02_medication_name_matching.py"
)


def load_matching_module():
    """Load the existing medication name matching implementation."""
    spec = importlib.util.spec_from_file_location(
        "medication_name_matching",
        MATCHING_SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module



def find_medication_mentions(query, medications, normalize_name):
    """Identify explicit medication mentions without overlapping matches."""
    normalized_query = normalize_name(query)
    candidates = []

    for normalized_name, medication in medications.items():
        if not normalized_name:
            continue

        pattern = (
            r"(?<!\w)"
            + re.escape(normalized_name)
            + r"(?!\w)"
        )

        for match in re.finditer(pattern, normalized_query):
            candidates.append({
                "name": medication["name"],
                "normalized_name": normalized_name,
                "document_ids": medication["document_ids"],
                "match_type": "explicit_mention",
                "similarity": 100.0,
                "start": match.start(),
                "end": match.end(),
            })

    candidates.sort(
        key=lambda item: (
            -(item["end"] - item["start"]),
            item["start"],
            item["normalized_name"],
        )
    )

    selected = []

    for candidate in candidates:
        overlaps = any(
            candidate["start"] < existing["end"]
            and candidate["end"] > existing["start"]
            for existing in selected
        )

        if not overlaps:
            selected.append(candidate)

    selected.sort(key=lambda item: item["start"])

    for entity in selected:
        entity.pop("start")
        entity.pop("end")

    return selected


def recognize_medication(query, medications, normalize_name):
    """Recognize medication entities without guessing unknown names."""
    mentions = find_medication_mentions(
        query,
        medications,
        normalize_name,
    )

    if not mentions:
        return {
            "query": query,
            "status": "no_explicit_match",
            "entities": [],
        }

    return {
        "query": query,
        "status": "matched",
        "entities": mentions,
    }


def main():
    matching = load_matching_module()
    medications = matching.load_medications()

    test_queries = [
        "aspirin",
        "Apakah loratadine aman untuk ibu hamil?",
        "What is the pregnancy safety information for naproxen?",
        "Is aspirin / dipyridamole safe during pregnancy?",
        "Can I take paracetamol and ibuprofen during pregnancy?",
        "Apakah loratadin aman untuk ibu hamil?",
    ]

    print("=== Medication Entity Recognition Test ===")
    print(f"Unique medication names: {len(medications)}")

    for query in test_queries:
        result = recognize_medication(
            query,
            medications,
            matching.normalize_name,
        )

        print(f"\nQuery: {query}")
        print(f"Status: {result['status']}")

        if not result["entities"]:
            print("Detected medications: None")
            continue

        for entity in result["entities"]:
            print(
                f"Detected: {entity['name']} "
                f"| Match: {entity['match_type']} "
                f"| Documents: {', '.join(entity['document_ids'])}"
            )


if __name__ == "__main__":
    main()

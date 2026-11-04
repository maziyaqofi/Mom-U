
import importlib.util
import re
from pathlib import Path

from rapidfuzz import fuzz, process


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RETRIEVAL_DIR = PROJECT_ROOT / "src/retrieval"

FUZZY_THRESHOLD = 80
MAX_SUGGESTIONS = 5


def load_module(filename, module_name):
    """Load an existing retrieval module."""
    path = RETRIEVAL_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_candidate_phrases(query, normalize_name):
    """Generate conservative phrases for fuzzy name matching."""
    normalized_query = normalize_name(query)

    phrases = [normalized_query]

    # Remove common dosage and formulation suffixes.
    cleaned = re.sub(
        r"\b\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml)\b",
        " ",
        normalized_query,
    )

    cleaned = re.sub(
        r"\b(?:tablets?|capsules?|film|coated)\b",
        " ",
        cleaned,
    )

    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if cleaned and cleaned not in phrases:
        phrases.append(cleaned)

    # Individual tokens are only candidate hints, not verified entities.
    for token in re.findall(r"[a-z][a-z0-9-]{3,}", cleaned):
        if token not in phrases:
            phrases.append(token)

    return phrases


def suggest_medications(
    query,
    medications,
    normalize_name,
    limit=MAX_SUGGESTIONS,
    threshold=FUZZY_THRESHOLD,
):
    """Generate fuzzy suggestions without confirming identity."""
    phrases = extract_candidate_phrases(query, normalize_name)
    medication_names = list(medications.keys())

    suggestions = {}

    for phrase in phrases:
        if len(phrase) < 4:
            continue

        matches = process.extract(
            phrase,
            medication_names,
            scorer=fuzz.ratio,
            limit=limit,
            score_cutoff=threshold,
        )

        for normalized_name, score, _ in matches:
            existing = suggestions.get(normalized_name)

            if existing is None or score > existing["similarity"]:
                suggestions[normalized_name] = {
                    "name": medications[normalized_name]["name"],
                    "document_ids": medications[normalized_name]["document_ids"],
                    "match_type": "fuzzy_suggestion",
                    "similarity": round(score, 2),
                    "matched_phrase": phrase,
                }

    ranked = sorted(
        suggestions.values(),
        key=lambda item: (
            -item["similarity"],
            item["name"].casefold(),
        ),
    )

    return ranked[:limit]


def resolve_medication(
    query,
    medications,
    matching_module,
    recognition_module,
):
    """Resolve explicit names or provide unconfirmed candidates."""
    recognition = recognition_module.recognize_medication(
        query,
        medications,
        matching_module.normalize_name,
    )

    if recognition["entities"]:
        return {
            "query": query,
            "status": "matched",
            "entities": recognition["entities"],
            "suggestions": [],
            "requires_confirmation": False,
        }

    suggestions = suggest_medications(
        query,
        medications,
        matching_module.normalize_name,
    )

    if suggestions:
        return {
            "query": query,
            "status": "confirmation_required",
            "entities": [],
            "suggestions": suggestions,
            "requires_confirmation": True,
        }

    return {
        "query": query,
        "status": "unresolved",
        "entities": [],
        "suggestions": [],
        "requires_confirmation": True,
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

    medications = matching.load_medications()

    test_queries = [
        "loratadine",
        "loratadin",
        "paracetmol",
        "Panadol",
        "PARACETAM0L 500 MG",
        "Apakah ibuprofen aman untuk ibu hamil?",
        "xyzmedication123",
    ]

    print("=== Medication Candidate Resolution Test ===")
    print(f"Unique medication names: {len(medications)}")

    for query in test_queries:
        result = resolve_medication(
            query,
            medications,
            matching,
            recognition,
        )

        print(f"\nQuery: {query}")
        print(f"Status: {result['status']}")
        print(
            f"Requires confirmation: "
            f"{result['requires_confirmation']}"
        )

        for entity in result["entities"]:
            print(
                f"Matched: {entity['name']} "
                f"| Documents: {', '.join(entity['document_ids'])}"
            )

        for suggestion in result["suggestions"]:
            print(
                f"Suggested: {suggestion['name']} "
                f"| Similarity: {suggestion['similarity']:.2f} "
                f"| Phrase: {suggestion['matched_phrase']}"
            )

        if not result["entities"] and not result["suggestions"]:
            print("No medication candidates found.")


if __name__ == "__main__":
    main()

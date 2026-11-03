
import json
import re
import unicodedata
from pathlib import Path

from rapidfuzz import fuzz, process


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORPUS_PATH = (
    PROJECT_ROOT / "data/processed/medication_corpus.jsonl"
)


def normalize_name(name):
    """Normalize medication names for string matching."""
    name = unicodedata.normalize("NFKC", name)
    name = name.casefold()
    name = re.sub(r"\s+", " ", name)
    return name.strip()


def load_medications():
    """Load unique medication names from the corpus."""
    medications = {}

    with CORPUS_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            document = json.loads(line)
            original_name = document["Name"]
            normalized_name = normalize_name(original_name)

            if not normalized_name:
                continue

            if normalized_name not in medications:
                medications[normalized_name] = {
                    "name": original_name,
                    "document_ids": [],
                }

            medications[normalized_name]["document_ids"].append(
                document["document_id"]
            )

    return medications


def exact_match(query, medications):
    """Find an exact normalized medication name."""
    normalized_query = normalize_name(query)

    if normalized_query in medications:
        return [{
            **medications[normalized_query],
            "match_type": "exact",
            "similarity": 100.0,
        }]

    return []


def prefix_match(query, medications, limit=5):
    """Find medication names beginning with the query."""
    normalized_query = normalize_name(query)

    if not normalized_query:
        return []

    matches = []

    for normalized_name, medication in medications.items():
        if normalized_name.startswith(normalized_query):
            matches.append({
                **medication,
                "match_type": "prefix",
                "similarity": 100.0,
            })

    matches.sort(key=lambda item: normalize_name(item["name"]))

    return matches[:limit]


def fuzzy_match(query, medications, limit=5, threshold=80):
    """Suggest medication names with similar spelling."""
    normalized_query = normalize_name(query)

    if len(normalized_query) < 3:
        return []

    candidates = process.extract(
        normalized_query,
        list(medications.keys()),
        scorer=fuzz.ratio,
        limit=limit,
        score_cutoff=threshold,
    )

    matches = []

    for normalized_name, score, _ in candidates:
        matches.append({
            **medications[normalized_name],
            "match_type": "fuzzy",
            "similarity": round(score, 2),
        })

    return matches


def search_medication(query, medications):
    """Search medication names using a staged matching strategy."""
    matches = exact_match(query, medications)

    if matches:
        return matches

    matches = prefix_match(query, medications)

    if matches:
        return matches

    return fuzzy_match(query, medications)


def main():
    print("Loading medication names...")
    medications = load_medications()

    print(f"Unique medication names: {len(medications)}")
    print("Medication name matching ready.")

    while True:
        query = input(
            "\nEnter medication name (or 'exit'): "
        ).strip()

        if query.casefold() == "exit":
            print("Exiting medication name matching.")
            break

        if len(query) < 2:
            print("Please enter at least 2 characters.")
            continue

        matches = search_medication(query, medications)

        if not matches:
            print("No medication name candidates found.")
            continue

        print("\n=== Medication Name Candidates ===")

        for rank, match in enumerate(matches, start=1):
            print(f"\nCandidate: {rank}")
            print(f"Medication: {match['name']}")
            print(f"Match Type: {match['match_type']}")
            print(f"Similarity: {match['similarity']:.2f}")
            print(
                "Related Document IDs: "
                + ", ".join(match["document_ids"])
            )

        print(
            "\nNote: Confirm the medication identity before "
            "retrieving pregnancy information."
        )


if __name__ == "__main__":
    main()

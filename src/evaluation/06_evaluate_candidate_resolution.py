
import csv
import importlib.util
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RETRIEVAL_DIR = PROJECT_ROOT / "src/retrieval"
DATASET_PATH = PROJECT_ROOT / "data/evaluation/robustness_queries.csv"
OUTPUT_DIR = PROJECT_ROOT / "reports/evaluation"


def load_module(filename, module_name):
    """Load a Python module from the retrieval directory."""
    path = RETRIEVAL_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_queries():
    """Load the existing robustness evaluation dataset."""
    with DATASET_PATH.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def parse_values(value):
    """Parse pipe-separated evaluation targets."""
    return [
        item.strip()
        for item in value.split("|")
        if item.strip()
    ]


def save_csv(path, rows, fieldnames):
    """Save evaluation results to a CSV file."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


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
    queries = load_queries()

    rows = []
    status_counts = Counter()

    print("=== EXP-004G Candidate Resolution Evaluation ===")
    print(f"Total queries: {len(queries)}")

    for query in queries:
        result = resolver.resolve_medication(
            query["query_text"],
            medications,
            matching,
            recognition,
        )

        expected = {
            matching.normalize_name(name)
            for name in parse_values(query["expected_medications"])
        }

        detected = {
            matching.normalize_name(entity["name"])
            for entity in result["entities"]
        }

        suggestions = [
            matching.normalize_name(item["name"])
            for item in result["suggestions"]
        ]

        entity_exact_match = detected == expected

        # Suggestion metrics apply only when a target exists
        # and the resolver did not recognize an explicit entity.
        suggestion_eligible = (
            bool(expected)
            and result["status"] != "matched"
        )

        suggestion_hit_1 = (
            int(bool(expected.intersection(suggestions[:1])))
            if suggestion_eligible
            else None
        )

        suggestion_hit_5 = (
            int(bool(expected.intersection(suggestions[:5])))
            if suggestion_eligible
            else None
        )

        # Any suggestion on a query with no expected medication
        # is flagged for manual false-positive review.
        unexpected_suggestions = (
            bool(suggestions) and not expected
        )

        status_counts[result["status"]] += 1

        row = {
            "query_id": query["query_id"],
            "query_type": query["query_type"],
            "query_text": query["query_text"],
            "evaluation_scope": query["evaluation_scope"],
            "expected_medications": "|".join(sorted(expected)),
            "detected_medications": "|".join(sorted(detected)),
            "suggested_medications": "|".join(suggestions),
            "resolution_status": result["status"],
            "requires_confirmation": int(
                result["requires_confirmation"]
            ),
            "entity_exact_match": int(entity_exact_match),
            "suggestion_eligible": int(suggestion_eligible),
            "suggestion_hit_at_1": suggestion_hit_1,
            "suggestion_hit_at_5": suggestion_hit_5,
            "unexpected_suggestions": int(
                unexpected_suggestions
            ),
        }

        rows.append(row)

        print(
            f"{query['query_id']} | "
            f"{query['query_type']:23s} | "
            f"Status: {result['status']:22s} | "
            f"Entity match: {entity_exact_match} | "
            f"Suggestion@1: {suggestion_hit_1}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    save_csv(
        OUTPUT_DIR / "candidate_resolution_results.csv",
        rows,
        list(rows[0].keys()),
    )

    eligible_rows = [
        row for row in rows if row["suggestion_eligible"]
    ]

    suggestion_hit_1 = (
        sum(row["suggestion_hit_at_1"] for row in eligible_rows)
        / len(eligible_rows)
        if eligible_rows
        else None
    )

    suggestion_hit_5 = (
        sum(row["suggestion_hit_at_5"] for row in eligible_rows)
        / len(eligible_rows)
        if eligible_rows
        else None
    )

    print("\n=== Summary ===")
    print(
        f"Exact entity-set matches: "
        f"{sum(row['entity_exact_match'] for row in rows)}"
        f"/{len(rows)}"
    )

    for status, count in sorted(status_counts.items()):
        print(f"{status}: {count}")

    print(
        f"Suggestion-eligible queries: {len(eligible_rows)}"
    )

    if suggestion_hit_1 is not None:
        print(f"Suggestion Hit@1: {suggestion_hit_1:.4f}")
        print(f"Suggestion Hit@5: {suggestion_hit_5:.4f}")
    else:
        print("Suggestion metrics: Not applicable")

    print(
        "Queries flagged for unexpected suggestions: "
        f"{sum(row['unexpected_suggestions'] for row in rows)}"
    )

    print(f"\nResults saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

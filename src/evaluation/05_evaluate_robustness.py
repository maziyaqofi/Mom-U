
import csv
import importlib.util
from collections import defaultdict
from pathlib import Path

from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RETRIEVAL_DIR = PROJECT_ROOT / "src/retrieval"
DATASET_PATH = PROJECT_ROOT / "data/evaluation/robustness_queries.csv"
OUTPUT_DIR = PROJECT_ROOT / "reports/evaluation"

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 10


def load_module(filename, module_name):
    """Load an existing retrieval module."""
    path = RETRIEVAL_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_queries():
    """Load robustness test cases."""
    with DATASET_PATH.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def parse_targets(value):
    """Parse pipe-separated targets."""
    return [item.strip() for item in value.split("|") if item.strip()]


def get_document_ids(results):
    """Extract document identifiers from ranked results."""
    return [item["document_id"] for item in results]


def calculate_target_coverage(targets, ranked_ids, k):
    """Measure the proportion of target documents found in top-k."""
    if not targets:
        return None

    return sum(
        target in ranked_ids[:k] for target in targets
    ) / len(targets)


def save_csv(path, rows, fieldnames):
    """Save structured evaluation output."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    matching = load_module(
        "02_medication_name_matching.py", "medication_matching"
    )
    recognition = load_module(
        "06_medication_entity_recognition.py", "medication_recognition"
    )
    bm25_module = load_module(
        "01_bm25_baseline.py", "bm25_baseline"
    )
    semantic_module = load_module(
        "04_semantic_retrieval.py", "semantic_retrieval"
    )
    hybrid_module = load_module(
        "05_hybrid_retrieval.py", "hybrid_retrieval"
    )
    entity_module = load_module(
        "07_entity_aware_retrieval.py", "entity_aware_retrieval"
    )

    print("Loading robustness dataset...")
    queries = load_queries()

    print("Loading medication corpus...")
    documents = bm25_module.load_corpus()
    medications = matching.load_medications()

    print("Building BM25 index...")
    bm25 = bm25_module.build_bm25(documents)

    print("Loading semantic model...")
    model = SentenceTransformer(MODEL_NAME)

    print("Loading document embeddings...")
    embeddings = hybrid_module.load_or_build_embeddings(
        documents, model, semantic_module
    )

    rows = []
    grouped = defaultdict(list)

    for query in queries:
        result = entity_module.entity_aware_search(
            query["query_text"],
            documents,
            bm25,
            embeddings,
            model,
            bm25_module,
            semantic_module,
            hybrid_module,
            recognition,
            medications,
            matching,
            top_k=TOP_K,
        )

        expected_names = parse_targets(query["expected_medications"])
        expected_ids = parse_targets(query["expected_document_ids"])

        detected_names = [
            matching.normalize_name(entity["name"])
            for entity in result["recognition"]["entities"]
        ]

        normalized_expected = [
            matching.normalize_name(name)
            for name in expected_names
        ]

        entity_exact_set_match = (
            set(detected_names) == set(normalized_expected)
        )

        hybrid_ids = get_document_ids(result["hybrid"])
        entity_ids = get_document_ids(result["entity_aware"])

        hybrid_coverage_1 = calculate_target_coverage(
            expected_ids, hybrid_ids, 1
        )
        hybrid_coverage_5 = calculate_target_coverage(
            expected_ids, hybrid_ids, 5
        )
        entity_coverage_1 = calculate_target_coverage(
            expected_ids, entity_ids, 1
        )
        entity_coverage_5 = calculate_target_coverage(
            expected_ids, entity_ids, 5
        )

        row = {
            "query_id": query["query_id"],
            "query_type": query["query_type"],
            "evaluation_scope": query["evaluation_scope"],
            "query_text": query["query_text"],
            "expected_medications": "|".join(expected_names),
            "detected_medications": "|".join(detected_names),
            "entity_exact_set_match": int(entity_exact_set_match),
            "hybrid_top_1": hybrid_ids[0] if hybrid_ids else "",
            "entity_aware_top_1": entity_ids[0] if entity_ids else "",
            "hybrid_target_coverage_at_1": hybrid_coverage_1,
            "hybrid_target_coverage_at_5": hybrid_coverage_5,
            "entity_target_coverage_at_1": entity_coverage_1,
            "entity_target_coverage_at_5": entity_coverage_5,
        }

        rows.append(row)
        grouped[query["query_type"]].append(row)

        print(
            f"{query['query_id']} | "
            f"{query['query_type']:23s} | "
            f"Entity match: {entity_exact_set_match} | "
            f"Hybrid@1: {hybrid_ids[0] if hybrid_ids else 'None'} | "
            f"Entity@1: {entity_ids[0] if entity_ids else 'None'}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    save_csv(
        OUTPUT_DIR / "robustness_results.csv",
        rows,
        list(rows[0].keys()),
    )

    print("\n=== Entity Recognition Summary ===")
    print(
        f"Exact entity-set matches: "
        f"{sum(row['entity_exact_set_match'] for row in rows)}"
        f"/{len(rows)}"
    )

    print("\n=== Results by Query Type ===")

    for query_type, group in sorted(grouped.items()):
        matched = sum(
            row["entity_exact_set_match"] for row in group
        )

        print(
            f"{query_type:23s} | "
            f"Entity matches: {matched}/{len(group)}"
        )

    print(f"\nResults saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

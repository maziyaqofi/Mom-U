
import csv
import importlib.util
from pathlib import Path

from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RETRIEVAL_DIR = PROJECT_ROOT / "src/retrieval"
EVALUATION_DIR = PROJECT_ROOT / "data/evaluation"
OUTPUT_DIR = PROJECT_ROOT / "reports/evaluation"

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 10


def load_module(filename, module_name):
    """Load a Python module from the retrieval directory."""
    path = RETRIEVAL_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_queries():
    """Load the existing medication target evaluation queries."""
    path = EVALUATION_DIR / "evaluation_queries.csv"

    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def target_rank(results, target_document_id):
    """Return the target rank within the evaluated result list."""
    for rank, result in enumerate(results, start=1):
        if result["document_id"] == target_document_id:
            return rank

    return None


def calculate_metrics(ranks):
    """Calculate target retrieval metrics."""
    total = len(ranks)

    return {
        "hit_at_1": sum(r == 1 for r in ranks) / total,
        "hit_at_5": sum(
            r is not None and r <= 5 for r in ranks
        ) / total,
        "hit_at_10": sum(
            r is not None and r <= 10 for r in ranks
        ) / total,
        "mrr_at_10": sum(
            1 / r if r is not None and r <= 10 else 0
            for r in ranks
        ) / total,
    }


def save_csv(path, rows, fieldnames):
    """Write evaluation results to a CSV file."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    bm25_module = load_module(
        "01_bm25_baseline.py", "bm25_baseline"
    )
    semantic_module = load_module(
        "04_semantic_retrieval.py", "semantic_retrieval"
    )
    hybrid_module = load_module(
        "05_hybrid_retrieval.py", "hybrid_retrieval"
    )
    matching_module = load_module(
        "02_medication_name_matching.py", "medication_matching"
    )
    recognition_module = load_module(
        "06_medication_entity_recognition.py", "medication_recognition"
    )
    entity_module = load_module(
        "07_entity_aware_retrieval.py", "entity_aware_retrieval"
    )

    print("Loading corpus and evaluation queries...")
    documents = bm25_module.load_corpus()
    queries = load_queries()
    medications = matching_module.load_medications()

    print("Building BM25 index...")
    bm25 = bm25_module.build_bm25(documents)

    print("Loading semantic model...")
    model = SentenceTransformer(MODEL_NAME)

    print("Loading document embeddings...")
    embeddings = hybrid_module.load_or_build_embeddings(
        documents, model, semantic_module
    )

    result_rows = []
    ranks_by_method = {
        "hybrid": [],
        "entity_aware": [],
    }

    for query in queries:
        query_id = query["query_id"]
        query_text = query["query_text"]
        target_id = query["target_document_id"]

        results = entity_module.entity_aware_search(
            query_text,
            documents,
            bm25,
            embeddings,
            model,
            bm25_module,
            semantic_module,
            hybrid_module,
            recognition_module,
            medications,
            matching_module,
            top_k=TOP_K,
        )

        for method in ("hybrid", "entity_aware"):
            rank = target_rank(results[method], target_id)
            ranks_by_method[method].append(rank)

            result_rows.append({
                "query_id": query_id,
                "query_type": query["query_type"],
                "query_text": query_text,
                "method": method,
                "target_document_id": target_id,
                "target_rank": rank if rank is not None else "",
                "hit_at_1": int(rank == 1),
                "hit_at_5": int(
                    rank is not None and rank <= 5
                ),
                "hit_at_10": int(
                    rank is not None and rank <= 10
                ),
                "reciprocal_rank_at_10": (
                    1 / rank
                    if rank is not None and rank <= 10
                    else 0
                ),
            })

    summary_rows = []

    print("\n=== EXP-004D Evaluation Results ===")

    for method, ranks in ranks_by_method.items():
        metrics = calculate_metrics(ranks)

        summary_rows.append({
            "method": method,
            "query_count": len(ranks),
            **metrics,
        })

        print(
            f"{method:15s} | "
            f"Hit@1: {metrics['hit_at_1']:.4f} | "
            f"Hit@5: {metrics['hit_at_5']:.4f} | "
            f"Hit@10: {metrics['hit_at_10']:.4f} | "
            f"MRR@10: {metrics['mrr_at_10']:.4f}"
        )

    save_csv(
        OUTPUT_DIR / "entity_aware_results.csv",
        result_rows,
        [
            "query_id",
            "query_type",
            "query_text",
            "method",
            "target_document_id",
            "target_rank",
            "hit_at_1",
            "hit_at_5",
            "hit_at_10",
            "reciprocal_rank_at_10",
        ],
    )

    save_csv(
        OUTPUT_DIR / "entity_aware_summary.csv",
        summary_rows,
        [
            "method",
            "query_count",
            "hit_at_1",
            "hit_at_5",
            "hit_at_10",
            "mrr_at_10",
        ],
    )

    print(f"\nResults saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

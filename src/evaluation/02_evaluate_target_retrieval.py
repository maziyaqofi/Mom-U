
import csv
import sys
from collections import defaultdict
from pathlib import Path

from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RETRIEVAL_DIR = PROJECT_ROOT / "src/retrieval"

EVALUATION_PATH = (
    PROJECT_ROOT / "data/evaluation/evaluation_queries.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "reports/evaluation"

TOP_K = 10

METHODS = ["bm25", "semantic", "hybrid"]


def load_hybrid_module():
    """Import the existing hybrid retrieval implementation."""
    sys.path.insert(0, str(RETRIEVAL_DIR))

    import importlib.util

    module_path = RETRIEVAL_DIR / "05_hybrid_retrieval.py"

    spec = importlib.util.spec_from_file_location(
        "hybrid_retrieval",
        module_path,
    )

    if spec is None or spec.loader is None:
        raise ImportError("Cannot load hybrid retrieval module")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def load_queries():
    """Load evaluation queries and their validated targets."""
    with EVALUATION_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def get_target_rank(results, target_document_id):
    """Find the target document rank within retrieved results."""
    for rank, result in enumerate(results, start=1):
        if result["document_id"] == target_document_id:
            return rank

    return None


def evaluate_query(query_record, retrieved):
    """Evaluate a single query across retrieval methods."""
    rows = []

    for method in METHODS:
        rank = get_target_rank(
            retrieved[method],
            query_record["target_document_id"],
        )

        rows.append({
            "query_id": query_record["query_id"],
            "query_type": query_record["query_type"],
            "language": query_record["language"],
            "query_text": query_record["query_text"],
            "target_document_id": (
                query_record["target_document_id"]
            ),
            "method": method,
            "target_rank": rank if rank is not None else "",
            "hit_at_1": int(rank == 1),
            "hit_at_5": int(
                rank is not None and rank <= 5
            ),
            "hit_at_10": int(rank is not None),
            "reciprocal_rank_at_10": (
                1.0 / rank if rank is not None else 0.0
            ),
        })

    return rows


def summarize_results(rows, group_by=None):
    """Calculate mean target retrieval metrics."""
    groups = defaultdict(list)

    for row in rows:
        key = (
            (row["method"], row[group_by])
            if group_by
            else (row["method"],)
        )

        groups[key].append(row)

    summaries = []

    for key, group_rows in sorted(groups.items()):
        count = len(group_rows)

        summary = {
            "method": key[0],
            "query_type": key[1] if group_by else "all",
            "query_count": count,
            "hit_at_1": sum(
                row["hit_at_1"] for row in group_rows
            ) / count,
            "hit_at_5": sum(
                row["hit_at_5"] for row in group_rows
            ) / count,
            "hit_at_10": sum(
                row["hit_at_10"] for row in group_rows
            ) / count,
            "mrr_at_10": sum(
                row["reciprocal_rank_at_10"]
                for row in group_rows
            ) / count,
        }

        summaries.append(summary)

    return summaries


def save_csv(path, rows):
    """Save evaluation records as CSV."""
    if not rows:
        return

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys()),
        )

        writer.writeheader()
        writer.writerows(rows)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    hybrid = load_hybrid_module()

    bm25_module = hybrid.load_module(
        "01_bm25_baseline.py",
        "bm25_baseline",
    )

    semantic_module = hybrid.load_module(
        "04_semantic_retrieval.py",
        "semantic_retrieval",
    )

    print("Loading evaluation queries...")
    queries = load_queries()
    print(f"Total queries: {len(queries)}")

    print("Loading medication corpus...")
    documents = bm25_module.load_corpus()
    print(f"Total documents: {len(documents)}")

    print("Building BM25 index...")
    bm25 = bm25_module.build_bm25(documents)

    print("Loading Sentence-BERT model...")
    model = SentenceTransformer(hybrid.MODEL_NAME)

    embeddings = hybrid.load_or_build_embeddings(
        documents,
        model,
        semantic_module,
    )

    evaluation_rows = []

    for index, query_record in enumerate(queries, start=1):
        query_text = query_record["query_text"]

        retrieved = hybrid.hybrid_search(
            query=query_text,
            documents=documents,
            bm25=bm25,
            embeddings=embeddings,
            model=model,
            bm25_module=bm25_module,
            semantic_module=semantic_module,
            top_k=TOP_K,
        )

        rows = evaluate_query(query_record, retrieved)
        evaluation_rows.extend(rows)

        print(
            f"[{index:02d}/{len(queries)}] "
            f"{query_record['query_id']} "
            f"- {query_text}"
        )

    overall_summary = summarize_results(
        evaluation_rows,
    )

    category_summary = summarize_results(
        evaluation_rows,
        group_by="query_type",
    )

    save_csv(
        OUTPUT_DIR / "target_retrieval_results.csv",
        evaluation_rows,
    )

    save_csv(
        OUTPUT_DIR / "target_retrieval_summary.csv",
        overall_summary,
    )

    save_csv(
        OUTPUT_DIR / "target_retrieval_by_query_type.csv",
        category_summary,
    )

    print("\n=== Overall Evaluation Results ===")

    for result in overall_summary:
        print(
            f"{result['method']:10s} | "
            f"Hit@1: {result['hit_at_1']:.4f} | "
            f"Hit@5: {result['hit_at_5']:.4f} | "
            f"Hit@10: {result['hit_at_10']:.4f} | "
            f"MRR@10: {result['mrr_at_10']:.4f}"
        )

    print(f"\nResults saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

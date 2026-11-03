
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RETRIEVAL_DIR = Path(__file__).resolve().parent

CORPUS_PATH = (
    PROJECT_ROOT / "data/processed/medication_corpus.jsonl"
)

CACHE_DIR = PROJECT_ROOT / "data/cache"

MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

CANDIDATE_K = 20
TOP_K = 5
RRF_K = 60


def load_module(filename, module_name):
    """Load an existing retrieval module by file path."""
    module_path = RETRIEVAL_DIR / filename

    spec = importlib.util.spec_from_file_location(
        module_name,
        module_path,
    )

    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module: {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def get_cache_path():
    """Generate a cache filename based on corpus and model."""
    corpus_hash = hashlib.sha256(
        CORPUS_PATH.read_bytes()
    ).hexdigest()[:16]

    model_hash = hashlib.sha256(
        MODEL_NAME.encode("utf-8")
    ).hexdigest()[:12]

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    return CACHE_DIR / (
        f"medication_embeddings_{corpus_hash}_{model_hash}.npy"
    )


def load_or_build_embeddings(documents, model, semantic_module):
    """Load cached embeddings or generate them if missing."""
    cache_path = get_cache_path()

    if cache_path.exists():
        print("Loading cached document embeddings...")
        embeddings = np.load(
            cache_path,
            allow_pickle=False,
        )

        if (
            embeddings.ndim == 2
            and embeddings.shape[0] == len(documents)
            and embeddings.shape[1] == 384
        ):
            print(f"Embedding shape: {embeddings.shape}")
            return embeddings

        print("Invalid embedding cache. Rebuilding...")

    print("Building document embeddings...")

    embeddings = semantic_module.build_embeddings(
        documents,
        model,
    )

    np.save(cache_path, embeddings)

    print(f"Embeddings saved to: {cache_path}")
    print(f"Embedding shape: {embeddings.shape}")

    return embeddings


def reciprocal_rank_fusion(result_lists, k=RRF_K):
    """Combine ranked retrieval lists using RRF."""
    fused_scores = {}
    documents_by_id = {}

    for results in result_lists:
        for rank, result in enumerate(results, start=1):
            document_id = result["document_id"]

            fused_scores[document_id] = (
                fused_scores.get(document_id, 0.0)
                + 1.0 / (k + rank)
            )

            documents_by_id[document_id] = result

    ranked_ids = sorted(
        fused_scores,
        key=lambda document_id: (
            -fused_scores[document_id],
            document_id,
        ),
    )

    fused_results = []

    for document_id in ranked_ids:
        result = documents_by_id[document_id]

        fused_results.append({
            "document_id": document_id,
            "name": result["name"],
            "category": result["category"],
            "score": fused_scores[document_id],
            "safety_statement": result["safety_statement"],
        })

    return fused_results


def hybrid_search(
    query,
    documents,
    bm25,
    embeddings,
    model,
    bm25_module,
    semantic_module,
    top_k=TOP_K,
):
    """Retrieve and fuse BM25 and semantic rankings."""
    bm25_results = bm25_module.search(
        query,
        documents,
        bm25,
        top_k=CANDIDATE_K,
    )

    semantic_results = semantic_module.semantic_search(
        query,
        documents,
        embeddings,
        model,
        top_k=CANDIDATE_K,
    )

    fused_results = reciprocal_rank_fusion(
        [bm25_results, semantic_results]
    )

    return {
        "bm25": bm25_results[:top_k],
        "semantic": semantic_results[:top_k],
        "hybrid": fused_results[:top_k],
    }


def print_results(title, results, score_label):
    """Display ranked medication documents."""
    print(f"\n=== {title} ===")

    if not results:
        print("No matching documents found.")
        return

    for rank, result in enumerate(results, start=1):
        print(f"\nRank: {rank}")
        print(f"Document ID: {result['document_id']}")
        print(f"Medication: {result['name']}")
        print(f"Category: {result['category']}")
        print(f"{score_label}: {result['score']:.4f}")

        statement = result["safety_statement"]

        print(
            "Safety Statement: "
            + (
                statement
                if statement
                else "Not available in this dataset."
            )
        )


def main():
    print("Loading retrieval modules...")

    bm25_module = load_module(
        "01_bm25_baseline.py",
        "bm25_baseline",
    )

    semantic_module = load_module(
        "04_semantic_retrieval.py",
        "semantic_retrieval",
    )

    print("Loading medication corpus...")
    documents = bm25_module.load_corpus()

    print(f"Total documents: {len(documents)}")

    print("Building BM25 index...")
    bm25 = bm25_module.build_bm25(documents)

    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    embeddings = load_or_build_embeddings(
        documents,
        model,
        semantic_module,
    )

    print("Hybrid retrieval ready.")

    while True:
        query = input(
            "\nEnter medication query (or 'exit'): "
        ).strip()

        if query.casefold() == "exit":
            break

        if not query:
            print("Please enter a query.")
            continue

        results = hybrid_search(
            query,
            documents,
            bm25,
            embeddings,
            model,
            bm25_module,
            semantic_module,
        )

        print_results(
            "BM25 Results",
            results["bm25"],
            "BM25 Score",
        )

        print_results(
            "Semantic Results",
            results["semantic"],
            "Similarity",
        )

        print_results(
            "Hybrid RRF Results",
            results["hybrid"],
            "RRF Score",
        )


if __name__ == "__main__":
    main()

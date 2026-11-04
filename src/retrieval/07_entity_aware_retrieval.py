
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


def entity_aware_rerank(results, entities):
    """Prioritize documents matching explicitly recognized medications."""
    if not entities:
        return results

    target_ids = set()

    for entity in entities:
        target_ids.update(entity["document_ids"])

    reranked = []

    for result in results:
        item = result.copy()
        item["entity_match"] = item["document_id"] in target_ids
        reranked.append(item)

    reranked.sort(
        key=lambda item: (
            not item["entity_match"],
            -item["score"],
            item["document_id"],
        )
    )

    return reranked


def entity_aware_search(
    query,
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
    top_k=5,
):
    """Run hybrid retrieval with medication identity reranking."""
    recognition = recognition_module.recognize_medication(
        query,
        medications,
        matching_module.normalize_name,
    )

    hybrid_results = hybrid_module.hybrid_search(
        query,
        documents,
        bm25,
        embeddings,
        model,
        bm25_module,
        semantic_module,
        top_k=20,
    )

    reranked = entity_aware_rerank(
        hybrid_results["hybrid"],
        recognition["entities"],
    )

    return {
        "recognition": recognition,
        "hybrid": hybrid_results["hybrid"][:top_k],
        "entity_aware": reranked[:top_k],
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
    bm25_module = load_module(
        "01_bm25_baseline.py",
        "bm25_baseline",
    )
    semantic_module = load_module(
        "04_semantic_retrieval.py",
        "semantic_retrieval",
    )
    hybrid_module = load_module(
        "05_hybrid_retrieval.py",
        "hybrid_retrieval",
    )

    print("Loading medication corpus...")
    documents = bm25_module.load_corpus()
    medications = matching.load_medications()

    print("Building BM25 index...")
    bm25 = bm25_module.build_bm25(documents)

    print("Loading semantic model...")
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    print("Loading or building document embeddings...")
    embeddings = hybrid_module.load_or_build_embeddings(
        documents,
        model,
        semantic_module,
    )

    queries = [
        "aspirin",
        "Apakah loratadine aman untuk ibu hamil?",
        "What is the pregnancy safety information for naproxen?",
        "Is aspirin / dipyridamole safe during pregnancy?",
        "Can I take paracetamol and ibuprofen during pregnancy?",
    ]

    for query in queries:
        result = entity_aware_search(
            query,
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
        )

        print(f"\n=== Query: {query} ===")

        entities = result["recognition"]["entities"]
        print(
            "Detected medications: "
            + (
                ", ".join(entity["name"] for entity in entities)
                if entities
                else "None"
            )
        )

        for method in ("hybrid", "entity_aware"):
            print(f"\n{method.upper()} RESULTS")

            for rank, item in enumerate(result[method], start=1):
                print(
                    f"{rank}. {item['name']} "
                    f"[{item['document_id']}] "
                    f"Score: {item['score']:.4f}"
                )


if __name__ == "__main__":
    main()

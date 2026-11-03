
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CORPUS_PATH = (
    PROJECT_ROOT / "data/processed/medication_corpus.jsonl"
)

MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


def load_corpus():
    """Load medication documents from the JSONL corpus."""
    documents = []

    with CORPUS_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            documents.append(json.loads(line))

    return documents


def build_embeddings(documents, model):
    """Encode and normalize all retrieval documents."""
    texts = [
        document["retrieval_text"]
        for document in documents
    ]

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embeddings


def semantic_search(
    query,
    documents,
    embeddings,
    model,
    top_k=5,
):
    """Rank documents using cosine similarity."""
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )[0]

    scores = embeddings @ query_embedding

    ranked_indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for index in ranked_indices:
        document = documents[int(index)]

        results.append({
            "document_id": document["document_id"],
            "name": document["Name"],
            "category": document["Category"],
            "score": float(scores[index]),
            "safety_statement": document["Safety statement"],
        })

    return results


def main():
    print("Loading medication corpus...")
    documents = load_corpus()

    print(f"Total documents: {len(documents)}")

    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    print("Building document embeddings...")
    embeddings = build_embeddings(documents, model)

    print(f"Embedding shape: {embeddings.shape}")
    print("Semantic retrieval ready.")

    while True:
        query = input(
            "\nEnter pregnancy medication query (or 'exit'): "
        ).strip()

        if query.casefold() == "exit":
            break

        if not query:
            print("Please enter a query.")
            continue

        results = semantic_search(
            query,
            documents,
            embeddings,
            model,
        )

        print("\n=== Semantic Search Results ===")

        for rank, result in enumerate(results, start=1):
            print(f"\nRank: {rank}")
            print(f"Document ID: {result['document_id']}")
            print(f"Medication: {result['name']}")
            print(f"Category: {result['category']}")
            print(f"Similarity: {result['score']:.4f}")

            statement = result["safety_statement"]

            print(
                "Safety Statement: "
                + (
                    statement
                    if statement
                    else "Not available in this dataset."
                )
            )


if __name__ == "__main__":
    main()

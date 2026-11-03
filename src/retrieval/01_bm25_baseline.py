
import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORPUS_PATH = (
    PROJECT_ROOT / "data/processed/medication_corpus.jsonl"
)


def tokenize(text):
    """Convert text into lowercase tokens."""
    return re.findall(r"\w+", text.casefold())


def load_corpus():
    """Load medication documents from the JSONL corpus."""
    documents = []

    with CORPUS_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            documents.append(json.loads(line))

    return documents


def build_bm25(documents):
    """Build the BM25 index."""
    tokenized_corpus = [
        tokenize(doc["retrieval_text"])
        for doc in documents
    ]

    return BM25Okapi(tokenized_corpus)


def search(query, documents, bm25, top_k=5):
    """Retrieve the highest-ranked medication documents."""
    query_tokens = tokenize(query)

    if not query_tokens:
        return []

    scores = bm25.get_scores(query_tokens)

    ranked_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )

    results = []

    for index in ranked_indices:
        if scores[index] <= 0:
            continue

        document = documents[index]

        results.append({
            "document_id": document["document_id"],
            "name": document["Name"],
            "category": document["Category"],
            "score": float(scores[index]),
            "safety_statement": document["Safety statement"],
        })

        if len(results) >= top_k:
            break

    return results


def main():
    print("Loading medication corpus...")
    documents = load_corpus()

    print(f"Total documents: {len(documents)}")

    print("Building BM25 index...")
    bm25 = build_bm25(documents)

    print("BM25 index ready.")

    while True:
        query = input("\nEnter medication query (or 'exit'): ").strip()

        if query.casefold() == "exit":
            break

        if len(query) < 2:
            print("Please enter at least 2 characters.")
            continue

        results = search(query, documents, bm25)

        if not results:
            print("No matching documents found.")
            continue

        print("\n=== Search Results ===")

        for rank, result in enumerate(results, start=1):
            print(f"\nRank: {rank}")
            print(f"Document ID: {result['document_id']}")
            print(f"Medication: {result['name']}")
            print(f"Category: {result['category']}")
            print(f"BM25 Score: {result['score']:.4f}")

            statement = result["safety_statement"]

            if statement:
                print(f"Safety Statement: {statement}")
            else:
                print("Safety Statement: Not available")


if __name__ == "__main__":
    main()

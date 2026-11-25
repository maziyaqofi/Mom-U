import importlib.util
import json
from pathlib import Path
from rank_bm25 import BM25Okapi

# Mengimpor fungsi tokenize_pregnancy_text dari 12_pregnancy_tokenizer.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOKENIZER_PATH = PROJECT_ROOT / "src" / "retrieval" / "12_pregnancy_tokenizer.py"

spec = importlib.util.spec_from_file_location("preg_tokenizer", TOKENIZER_PATH)
preg_tokenizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preg_tokenizer)
tokenize_pregnancy_text = preg_tokenizer.tokenize_pregnancy_text

CORPUS_PATH = PROJECT_ROOT / "data" / "processed" / "pregnancy_corpus.jsonl"


class PregnancyBM25Search:
    def __init__(self, corpus_path: Path = CORPUS_PATH):
        self.documents = []
        self.tokenized_corpus = []
        self.bm25 = None
        self._load_and_index(corpus_path)

    def _load_and_index(self, corpus_path: Path):
        if not corpus_path.exists():
            raise FileNotFoundError(f"Korpus tidak ditemukan di: {corpus_path}")

        with open(corpus_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                doc = json.loads(line.strip())
                
                # Penanganan missing value pada content
                title = doc.get("title") or ""
                category = doc.get("category") or ""
                content = doc.get("content") or ""
                
                # Gabungkan atribut teks untuk indeksasi yang kaya
                searchable_text = f"{title} {category} {content}".strip()
                tokens = tokenize_pregnancy_text(searchable_text)
                
                self.documents.append(doc)
                self.tokenized_corpus.append(tokens)

        self.bm25 = BM25Okapi(self.tokenized_corpus, k1=1.2, b=0.75)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        query_tokens = tokenize_pregnancy_text(query)
        if not query_tokens:
            return []

        scores = self.bm25.get_scores(query_tokens)
        ranked_indices = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )[:top_k]

        results = []
        for rank, idx in enumerate(ranked_indices, 1):
            score = float(scores[idx])
            if score <= 0:
                continue
            doc = self.documents[idx]
            results.append({
                "rank": rank,
                "document_id": doc.get("document_id", f"doc_{idx}"),
                "title": doc.get("title", "Untitled"),
                "category": doc.get("category", "General"),
                "source": doc.get("source", "Unknown"),
                "bm25_score": round(score, 4),
            })
        return results


if __name__ == "__main__":
    engine = PregnancyBM25Search()
    print(f"[+] Indeks BM25 selesai dibangun untuk {len(engine.documents)} dokumen.\n")

    test_queries = [
        "12 week scan",
        "20 weeks pregnant development",
        "prenatal care screening",
    ]

    for q in test_queries:
        print(f"=== Query: '{q}' ===")
        hits = engine.search(q, top_k=3)
        if not hits:
            print("  [-] Tidak ada dokumen cocok.\n")
            continue
        for h in hits:
            print(f"  #{h['rank']} [{h['bm25_score']}] {h['title']} ({h['category']}) - {h['source']}")
        print()
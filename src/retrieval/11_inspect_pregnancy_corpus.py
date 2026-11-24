import json
from pathlib import Path

corpus_path = Path("data/processed/pregnancy_corpus.jsonl")

def inspect_corpus():
    if not corpus_path.exists():
        print(f"[-] File tidak ditemukan: {corpus_path}")
        return

    docs = []
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                docs.append(json.loads(line.strip()))

    print(f"[+] Total dokumen kehamilan ditemukan: {len(docs)}\n")
    
    # Tampilkan struktur key dan 2 sampel awal
    if docs:
        print(f"[+] Struktur atribut (keys): {list(docs[0].keys())}\n")
        for i, doc in enumerate(docs[:2], 1):
            content = doc.get("content") or doc.get("summary") or doc.get("text") or ""
            print(f"--- Sampel #{i} ---")
            print(f"Title    : {doc.get('title', 'N/A')}")
            print(f"Category : {doc.get('category', 'N/A')}")
            print(f"Content  : {content[:150]}...\n")

if __name__ == "__main__":
    inspect_corpus()
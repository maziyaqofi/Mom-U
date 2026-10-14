# Mom-U

**Intelligent Maternal Health Information Retrieval System**

Mom-U is an academic information retrieval project designed to help pregnant users find trustworthy, understandable, English-language pregnancy education resources using natural-language questions.

## Research objective
Compare BM25 (lexical), Sentence-Transformer embeddings (semantic), and Reciprocal Rank Fusion (hybrid) for retrieving relevant pregnancy education documents.

## Scope (MVP)
- English questions and English source documents.
- Retrieve and rank evidence-based educational documents, with title, snippet, source, URL, and review date when available.
- Display source links and safety disclaimers; do not diagnose or provide personalized treatment.
- Evaluate retrieval against human-reviewed query-document relevance judgments.
- Optional answer synthesis is **out of scope for MVP** and requires separate groundedness and clinical-safety review.

## Planned stack
Python 3.11, pandas, rank-bm25, sentence-transformers, FAISS (optional for scale), ir-measures, Streamlit.

## Repository guide
- [Project plan](docs/PROJECT_PLAN.md)
- [Dataset collection protocol](docs/DATASET_COLLECTION.md)
- [Research and evaluation plan](docs/RESEARCH_PLAN.md)
- [Decision log](docs/DECISIONS.md)
- [Progress log](docs/PROGRESS_LOG.md)
- [Dataset example](data/README.md)

## Current status
**Planning stage.** No real corpus has been collected or validated yet. Example records are synthetic and for illustration only.

## Getting started
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ethical and content-use principles
Check license and permitted reuse per document. Cite original sources. Do not commit copyrighted full text without permission, private health data, or API credentials. Research articles are evidence sources, not automatically patient-facing guidance.

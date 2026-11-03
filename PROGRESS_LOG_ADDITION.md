## 2026-11-03 — Pregnancy Medication Semantic Retrieval

- Completed a Python 3.11 ML environment (`.venv-ml`) after resolving NumPy, PyTorch, Transformers, Sentence-Transformers, and Pandas compatibility issues.
- Successfully encoded all 1,778 TGA medication records with multilingual Sentence-BERT into 384-dimensional vectors.
- Ran four exploratory queries covering exact medication names, English pregnancy context, Indonesian cross-language retrieval, and broad pain-relief concepts.
- Recorded observed top-5 results and limitations in `reports/experiments/EXP-001_semantic_retrieval.md`.
- Remaining: Hybrid RRF, labeled relevance judgments, ranking metrics, and error analysis.
- Storage note: approximately 1.0 GiB remained free after clearing pip cache; reclaim additional disk space before installing more models.

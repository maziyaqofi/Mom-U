# Research and Evaluation Plan

## Research questions
RQ1: How does BM25 compare with semantic retrieval on natural-language pregnancy questions?
RQ2: Does rank-fusion hybrid retrieval improve retrieval quality over either individual method?
RQ3: What kinds of questions lead to retrieval errors or unsupported results?

## Methods
- BM25: token-based lexical retrieval.
- Semantic: English sentence-transformer embeddings with cosine similarity or normalized inner product.
- Hybrid: Reciprocal Rank Fusion of BM25 and semantic ranked lists.

## Ground truth
Create 30–50 realistic English queries. Pool candidate documents from all retrieval methods and assess query-document relevance using documented criteria (0=not relevant, 1=partially relevant, 2=highly relevant). Have clinical suitability independently checked for a subset or ideally all patient-facing materials. Avoid treating document topic labels as qrels.

## Metrics
Precision@5, Recall@5, MRR@10, nDCG@10, and search latency. Report aggregate scores, per-topic breakdowns, and qualitative failure cases. Explicitly state any limitations from incomplete pooling and judgments.

## Reproducibility
Fix model/version, preprocessing settings, corpus version, evaluation queries, qrels, and random seeds where applicable. Record all experimental changes in `docs/DECISIONS.md`.

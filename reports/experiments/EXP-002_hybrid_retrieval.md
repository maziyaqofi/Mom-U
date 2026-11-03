
# EXP-002 — Hybrid Medication Retrieval Using BM25, Sentence-BERT, and RRF

## 1. Experiment Information

| Field | Description |
|---|---|
| Project | Mom-U |
| Experiment ID | EXP-002 |
| Date | 2026-11-03 |
| Method | Hybrid Retrieval |
| Components | BM25, Multilingual Sentence-BERT, RRF |
| Status | Completed — Initial Testing |
| Implementation | `src/retrieval/05_hybrid_retrieval.py` |

## 2. Objectives

1. Integrate BM25 and multilingual Sentence-BERT.
2. Implement Reciprocal Rank Fusion (RRF).
3. Compare retrieval rankings across three methods.
4. Examine medication-specific, multilingual, and conceptual queries.
5. Identify limitations before formal evaluation.

## 3. Dataset

- Source: Australian TGA Pregnancy Medication Database
- Corpus: `data/processed/medication_corpus.jsonl`
- Documents: 1,778
- Embedding dimensions: 384

The same processed corpus was used for all three retrieval methods.

## 4. Methodology

### 4.1 BM25

BM25 ranks documents using lexical matching between query terms and document text.

### 4.2 Sentence-BERT

The multilingual model `paraphrase-multilingual-MiniLM-L12-v2` represents queries and documents as embeddings.

Cosine similarity is used for ranking.

### 4.3 Reciprocal Rank Fusion

The RRF formula is:

\[
RRF(d) = \sum_{r \in R} \frac{1}{k + rank_r(d)}
\]

Configuration:

| Parameter | Value |
|---|---|
| RRF constant | 60 |
| BM25 candidates | Top 20 |
| Semantic candidates | Top 20 |
| Final results | Top 5 |
| Fusion weighting | Equal |

RRF combines rankings without directly comparing BM25 scores and cosine similarities.

## 5. Implementation Results

The implementation successfully:

- Loaded 1,778 medication documents.
- Built the BM25 index.
- Loaded the multilingual Sentence-BERT model.
- Generated document embeddings of shape `(1778, 384)`.
- Saved embeddings to a local cache.
- Reused cached embeddings during subsequent execution.
- Produced BM25, semantic, and hybrid rankings.

The initial embedding generation took approximately 30 seconds.

A Hugging Face `FutureWarning` appeared but did not interrupt execution.

## 6. Test Queries

| ID | Query | Type |
|---|---|---|
| Q01 | paracetamol | Exact medication name |
| Q02 | ibuprofen during pregnancy | Medication with pregnancy context |
| Q03 | Apakah ibuprofen aman untuk ibu hamil? | Indonesian multilingual query |
| Q04 | pain relief medication during pregnancy | Concept-based query |

## 7. Top-1 Comparison

| Query | BM25 | Sentence-BERT | Hybrid RRF |
|---|---|---|---|
| Q01 | paracetamol | paracetamol | paracetamol |
| Q02 | ibuprofen | ibuprofen | ibuprofen |
| Q03 | ibuprofen | ibuprofen | ibuprofen |
| Q04 | abaloparatide | paracetamol | bethanechol |

## 8. Detailed Observations

### Q01 — Paracetamol

All methods ranked paracetamol first.

BM25 returned one matching document.

Semantic retrieval returned additional documents with limited apparent relevance.

Hybrid RRF preserved the target at rank 1 but also included unrelated semantic candidates.

**Finding:** Hybrid retrieval did not demonstrate an obvious advantage over exact lexical matching.

### Q02 — Ibuprofen During Pregnancy

All methods ranked ibuprofen first.

BM25 also retrieved documents such as abaloparatide and metformin because their safety statements contained pregnancy-related terminology.

Semantic retrieval included several related medications but also some potentially irrelevant results.

Hybrid RRF ranked:

1. Ibuprofen
2. Abaloparatide
3. Flurbiprofen
4. Ibutilide
5. Metformin

**Finding:** Hybrid retrieval preserved the target medication but inherited irrelevant candidates from the lexical ranking.

### Q03 — Indonesian Ibuprofen Query

All methods ranked ibuprofen first.

BM25 primarily matched the medication name.

Sentence-BERT retrieved additional NSAID-related documents.

Hybrid RRF produced a ranking similar to semantic retrieval.

**Finding:** Multilingual semantic retrieval contributed substantially to the broader results for the Indonesian query.

### Q04 — Pain Relief Medication During Pregnancy

BM25 Top-5:

1. Abaloparatide
2. Metformin
3. Repaglinide
4. Alogliptin / metformin
5. Linagliptin / metformin

Sentence-BERT Top-5:

1. Paracetamol
2. Flurbiprofen
3. Safinamide
4. Diazoxide
5. Neostigmine

Hybrid RRF Top-5:

1. Bethanechol
2. Abaloparatide
3. Paracetamol
4. Flurbiprofen
5. Metformin

The hybrid method ranked bethanechol first despite its limited relevance to the requested pain-relief concept.

Paracetamol appeared at rank 1 in semantic retrieval but rank 3 in hybrid retrieval.

**Finding:** Standard RRF did not improve this concept-based query and introduced a less relevant top-ranked result.

## 9. Key Findings

1. The hybrid retrieval pipeline was implemented successfully.
2. Embedding caching reduced repeated computation.
3. All methods retrieved the target medication at rank 1 for three medication-specific queries.
4. Sentence-BERT produced the most relevant top-ranked result for the tested pain-relief query.
5. BM25 was influenced by common pregnancy-related terminology.
6. RRF inherited irrelevant documents from the component rankings.
7. Standard RRF was not consistently better than semantic retrieval in the initial tests.

## 10. Limitations

- Only four queries were tested.
- Relevance judgments were qualitative.
- No complete relevance annotation set was available.
- Precision@K, Recall@K, MRR, and nDCG were not calculated.
- No statistical significance testing was performed.
- The experiment did not assess clinical safety or medical recommendation accuracy.
- RRF candidate depth and weighting were not tuned.

## 11. Proposed Improvements

Potential improvements for future experiments include:

1. Medication entity recognition and exact-name matching.
2. Query intent classification.
3. Query-specific lexical filtering.
4. Weighted or adaptive rank fusion.
5. Expanded multilingual evaluation queries.
6. Relevance-based reranking.

These improvements are hypotheses and require independent evaluation.

## 12. Next Experiment

**EXP-003 — Retrieval Performance Evaluation**

Planned activities:

1. Construct a representative query dataset.
2. Annotate relevant medication documents.
3. Compare BM25, Sentence-BERT, and Hybrid RRF.
4. Calculate Precision@K, Recall@K, MRR, and nDCG.
5. Analyze performance by query type.

## 13. Conclusion

Hybrid retrieval using BM25, multilingual Sentence-BERT, and Reciprocal Rank Fusion was successfully implemented.

The initial experiments demonstrated reliable target retrieval for the tested medication-specific queries.

However, standard RRF did not consistently improve ranking relevance. In the concept-based query, it ranked bethanechol above paracetamol despite paracetamol being a more relevant result.

These findings motivate formal evaluation and further investigation of query-aware retrieval strategies.

The system remains an experimental information retrieval prototype and is not a validated clinical decision-support tool.

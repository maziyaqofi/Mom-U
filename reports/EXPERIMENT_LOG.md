
# Mom-U — Experiment Log

## 1. Project Overview

**Project Name:** Mom-U  
**Domain:** Pregnancy Health Information Retrieval  
**Current Focus:** Pregnancy Medication Information Retrieval  
**Documentation Format:** Markdown  
**Last Updated:** 2026-11-03

Mom-U is an information retrieval project designed to support pregnancy-related information access through multiple retrieval techniques.

This document tracks experiments, implementation progress, technical findings, and future evaluation plans.

Detailed experiment reports are stored in the `reports/experiments/` directory.

## 2. Experiment Registry

| ID | Experiment | Method | Status | Report |
|---|---|---|---|---|
| EXP-001 | Semantic Medication Retrieval | Multilingual Sentence-BERT | Completed — Initial Testing | [EXP-001](experiments/EXP-001_semantic_retrieval.md) |
| EXP-002 | Hybrid Medication Retrieval | BM25 + Sentence-BERT + RRF | Planned | Not available |
| EXP-003 | Retrieval Performance Evaluation | Precision@K, Recall@K, MRR, nDCG | Planned | Not available |
| EXP-004 | Retrieval Error Analysis | Query and Ranking Analysis | Planned | Not available |

## 3. Completed Implementation Milestones

### 3.1 Medication Dataset Preparation

**Status:** Completed

Implementation:

`src/data_processing/01_prepare_medication_corpus.py`

Outputs:

- `data/processed/medication_corpus.csv`
- `data/processed/medication_corpus.jsonl`
- `reports/medication_dataset_feasibility.json`

Key results:

- 1,778 medication records processed.
- 1,725 unique normalized medication names.
- 796 records with safety statements.
- 982 records without safety statements.

### 3.2 BM25 Baseline Retrieval

**Status:** Implemented and Functionally Tested

Implementation:

`src/retrieval/01_bm25_baseline.py`

Method:

BM25 keyword-based document ranking.

Observations:

- Exact medication terms can retrieve relevant documents.
- Partial tokens may not match full medication names.
- Retrieval depends on lexical overlap.

Formal evaluation remains pending.

### 3.3 Medication Name Matching

**Status:** Implemented and Functionally Tested

Implementation:

`src/retrieval/02_medication_name_matching.py`

Methods:

- Exact matching
- Prefix matching
- Fuzzy matching

Library:

RapidFuzz

Observations:

- Exact medication names can be resolved.
- Prefix matching supports partial names.
- Fuzzy matching supports some spelling variations.

### 3.4 Medication Detail Retrieval

**Status:** Implemented and Functionally Tested

Implementation:

`src/retrieval/03_medication_detail.py`

Features:

- Document ID lookup
- Medication name display
- Pregnancy category display
- Safety statement retrieval

Important limitation:

Missing safety statements must be reported explicitly and must not be interpreted as evidence of medication safety.

### 3.5 Semantic Retrieval

**Status:** Completed — Initial Testing

Experiment:

EXP-001

Implementation:

`src/retrieval/04_semantic_retrieval.py`

Model:

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

Key results:

- 1,778 document embeddings generated.
- Embedding dimensions: 384.
- Four initial queries tested.
- Exact medication queries retrieved expected medications.
- One Indonesian cross-language query successfully retrieved its target.
- General concept-based retrieval produced some irrelevant results.

Detailed report:

[EXP-001 — Semantic Retrieval](experiments/EXP-001_semantic_retrieval.md)

## 4. Current Technical Environment

| Component | Version |
|---|---|
| Python | 3.11.16 |
| NumPy | 1.26.4 |
| Pandas | 2.2.3 |
| PyTorch | 2.2.2 |
| Transformers | 4.41.2 |
| Sentence-Transformers | 3.0.1 |

Virtual environment:

`.venv-ml`

Validation:

```text
No broken requirements found.
```

## 5. Experiment Findings

### Finding 1 — Medication Identity Matters

Semantic similarity is useful for retrieval but does not guarantee exact medication identity.

Exact, prefix, and fuzzy matching remain important components.

### Finding 2 — Multilingual Retrieval Is Promising

The Indonesian ibuprofen query successfully retrieved the target English-language document.

Additional multilingual test cases are required before generalizing this finding.

### Finding 3 — Broad Queries Require Better Ranking

Concept-based queries may retrieve documents that are only weakly related to the intended information need.

Hybrid retrieval will be investigated as a possible improvement.

### Finding 4 — Dataset Completeness Is Limited

A substantial portion of the medication corpus does not contain safety statements.

The system must distinguish between missing information and verified medical evidence.

## 6. Planned Experiments

### EXP-002 — Hybrid Retrieval
| EXP-002 | Hybrid Medication Retrieval | BM25 + Sentence-BERT + RRF | Completed — Initial Testing | [EXP-002](experiments/EXP-002_hybrid_retrieval.md) |

**Status:** Planned

Objectives:

- Combine BM25 and Sentence-BERT.
- Implement Reciprocal Rank Fusion.
- Compare top-ranked documents.
- Examine exact-name, multilingual, and concept-based queries.

Planned implementation:

`src/retrieval/05_hybrid_retrieval.py`

### EXP-003 — Retrieval Evaluation
| EXP-003 | Medication Target Retrieval Evaluation | BM25 vs Sentence-BERT vs Hybrid RRF | Completed — Initial Evaluation | [EXP-003](experiments/EXP-003_retrieval_evaluation.md) |

**Status:** Planned

Objectives:

- Develop a representative evaluation query set.
- Define document relevance labels.
- Evaluate BM25, Sentence-BERT, and Hybrid RRF.
- Calculate Precision@K, Recall@K, MRR, and nDCG.
- Compare performance across query categories.

### EXP-004 — Retrieval Error Analysis

**Status:** Planned

Objectives:

- Analyze irrelevant retrieval results.
- Identify medication-name ambiguity.
- Examine spelling variations.
- Evaluate multilingual query failures.
- Investigate the impact of missing safety statements.

## 7. Documentation Guidelines

Each experiment should document:

1. Experiment ID and date.
2. Research objective.
3. Dataset and preprocessing.
4. Model or retrieval method.
5. Environment and dependencies.
6. Experimental procedure.
7. Queries and expected behavior.
8. Actual retrieval results.
9. Observations and analysis.
10. Technical issues and resolutions.
11. Limitations.
12. Conclusions and next steps.

All experiment documentation should be written in English.

## 8. Important Research Notes

- Retrieval similarity is not a medication safety score.
- TGA pregnancy categories must not be treated as ordinal risk scores.
- Missing safety statements do not indicate that a medication is safe.
- Retrieved information should preserve its source context.
- Medical claims require appropriate source verification.
- Qualitative observations should not be presented as formal evaluation metrics.
- Model improvements should be assessed using the same evaluation dataset.

## 9. Next Action

Implement EXP-002:

**Hybrid Medication Retrieval Using BM25, Sentence-BERT, and Reciprocal Rank Fusion.**

The next experiment should use the same medication corpus and initial test queries to support comparison with EXP-001.

Formal quantitative comparison will follow after relevance annotations have been prepared.
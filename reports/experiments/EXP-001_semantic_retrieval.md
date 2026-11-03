
# EXP-001 — Semantic Retrieval Using Multilingual Sentence-BERT

## 1. Experiment Information

| Field | Description |
|---|---|
| Project | Mom-U |
| Module | Pregnancy Medication Information Retrieval |
| Experiment ID | EXP-001 |
| Experiment Date | 2026-11-03 |
| Method | Semantic Retrieval |
| Model | paraphrase-multilingual-MiniLM-L12-v2 |
| Status | Completed — Initial Testing |
| Implementation | `src/retrieval/04_semantic_retrieval.py` |

## 2. Background

Mom-U is a pregnancy-focused information retrieval project designed to help users retrieve relevant information from structured and unstructured pregnancy-related data.

The Pregnancy Medication Information Retrieval module uses medication information from the Australian Therapeutic Goods Administration (TGA) pregnancy medication database.

Previous development stages successfully implemented:

1. Medication dataset preparation and validation.
2. BM25 keyword-based retrieval.
3. Exact, prefix, and fuzzy medication name matching.
4. Medication detail retrieval.

This experiment introduces semantic retrieval using a multilingual Sentence-BERT model.

Unlike traditional keyword-based retrieval, semantic retrieval represents text as numerical vectors (embeddings) and ranks documents based on semantic similarity.

## 3. Experiment Objectives

The experiment aims to:

1. Implement multilingual Sentence-BERT for medication document retrieval.
2. Generate embeddings for the medication corpus.
3. Test medication name retrieval.
4. Evaluate English pregnancy-related queries.
5. Test cross-language retrieval using Indonesian queries.
6. Observe retrieval behavior for general medication concepts.
7. Identify limitations for future hybrid retrieval development.

## 4. Dataset Description

### 4.1 Dataset Source

- Organization: Therapeutic Goods Administration (TGA), Australia
- Dataset: Pregnancy Medication Database
- Source file: `data/raw/medicines-pregnancy-current-database-2026-10-21.csv`
- Processed corpus: `data/processed/medication_corpus.jsonl`

### 4.2 Dataset Characteristics

| Attribute | Value |
|---|---|
| Total medication records | 1,778 |
| Unique normalized medication names | 1,725 |
| Records with safety statements | 796 |
| Records without safety statements | 982 |
| Source columns | 6 |
| Document ID format | TGA_XXXXX |

The original dataset includes:

- Name
- Category
- Safety statement
- Classification 1
- Classification 2
- Classification 3

The preprocessing stage generates normalized medication names and retrieval text for information retrieval experiments.

### 4.3 Dataset Limitations

Approximately 55.2% of the processed records do not contain a safety statement.

Missing safety statements must not be interpreted as evidence that a medication is safe during pregnancy.

TGA pregnancy categories are regulatory classifications and must not be interpreted as numerical safety scores.

## 5. Experiment Environment

### 5.1 Hardware and Operating System

- Operating system: macOS
- Architecture: Intel x86_64
- Execution environment: Local Python virtual environment
- Virtual environment: `.venv-ml`

### 5.2 Software Dependencies

| Library | Version |
|---|---|
| Python | 3.11.16 |
| NumPy | 1.26.4 |
| Pandas | 2.2.3 |
| PyTorch | 2.2.2 |
| Transformers | 4.41.2 |
| Sentence-Transformers | 3.0.1 |

Dependency validation:

```text
No broken requirements found.
```

### 5.3 Retrieval Configuration

| Parameter | Value |
|---|---|
| Embedding model | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| Retrieval approach | Dense semantic retrieval |
| Similarity metric | Cosine similarity |
| Total documents | 1,778 |
| Embedding dimensions | 384 |
| Number of encoding batches | 56 |
| Retrieved documents | Top 5 |

## 6. Experiment Procedure

### Step 1 — Load Medication Corpus

The processed medication corpus is loaded from the JSONL dataset.

Observed output:

```text
Loading medication corpus...
Total documents: 1778
```

### Step 2 — Load Sentence-BERT Model

The multilingual Sentence-BERT model is loaded using Sentence-Transformers.

```text
Loading model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

The model was downloaded and cached locally.

### Step 3 — Generate Document Embeddings

The model converts medication retrieval text into dense vector representations.

Observed output:

```text
Building document embeddings...
Batches: 100% | 56/56 [00:33]
Embedding shape: (1778, 384)
Semantic retrieval ready.
```

The encoding process completed in approximately 33 seconds during the recorded successful run.

### Step 4 — Execute Test Queries

Four queries were selected to examine different retrieval behaviors:

| Query ID | Query | Test Category |
|---|---|---|
| Q01 | paracetamol | Exact medication name |
| Q02 | ibuprofen during pregnancy | Medication and pregnancy context |
| Q03 | Apakah ibuprofen aman untuk ibu hamil? | Indonesian cross-language retrieval |
| Q04 | pain relief medication during pregnancy | Concept-based retrieval |

## 7. Experiment Results

### 7.1 Q01 — Exact Medication Name

**Query:** `paracetamol`

| Rank | Document ID | Medication | Category | Similarity |
|---|---|---|---|---|
| 1 | TGA_01250 | paracetamol | A | 0.5675 |
| 2 | TGA_01252 | paraldehyde | D | 0.5045 |
| 3 | TGA_00715 | fluticasone propionate / eformoterol fumarate | B3 | 0.4679 |
| 4 | TGA_00716 | fluticasone propionate / salmeterol xinafoate | B3 | 0.4642 |
| 5 | TGA_01356 | prilocaine (with or without felypressin) | A | 0.4583 |

**Observations:**

- The target medication was retrieved at rank 1.
- The top-ranked document matched the medication name exactly.
- Lower-ranked results included medications with limited apparent relevance.
- The target document did not contain a safety statement.

**Preliminary interpretation:**

Sentence-BERT successfully retrieved the target medication. However, exact medication lookup may benefit from explicit name matching rather than relying exclusively on semantic similarity.

### 7.2 Q02 — English Medication Query

**Query:** `ibuprofen during pregnancy`

| Rank | Document ID | Medication | Category | Similarity |
|---|---|---|---|---|
| 1 | TGA_00831 | ibuprofen | C | 0.7807 |
| 2 | TGA_00711 | flurbiprofen | C | 0.7379 |
| 3 | TGA_00832 | ibutilide | B3 | 0.7130 |
| 4 | TGA_00830 | ibrutinib | D | 0.6921 |
| 5 | TGA_00923 | ketoprofen | C | 0.6872 |

**Observations:**

- Ibuprofen was correctly retrieved at rank 1.
- Flurbiprofen and ketoprofen were also retrieved.
- Some results, including ibutilide and ibrutinib, were not clearly relevant to the intended medication.
- The ibuprofen document contained an NSAID-related pregnancy safety statement.

**Preliminary interpretation:**

The model retrieved the target medication and several related documents. However, semantic similarity alone did not eliminate potentially irrelevant medications.

### 7.3 Q03 — Indonesian Cross-Language Query

**Query:** `Apakah ibuprofen aman untuk ibu hamil?`

| Rank | Document ID | Medication | Category | Similarity |
|---|---|---|---|---|
| 1 | TGA_00831 | ibuprofen | C | 0.8042 |
| 2 | TGA_00711 | flurbiprofen | C | 0.7725 |
| 3 | TGA_01721 | valdecoxib | C | 0.7373 |
| 4 | TGA_01631 | tiaprofenic acid | C | 0.7339 |
| 5 | TGA_00923 | ketoprofen | C | 0.7300 |

**Observations:**

- The Indonesian query retrieved the English-language ibuprofen document at rank 1.
- Other retrieved documents included several NSAID-related medications.
- The query achieved a cosine similarity of 0.8042 for the target medication.
- The results demonstrate successful cross-language retrieval for this specific test case.

**Preliminary interpretation:**

Multilingual Sentence-BERT shows promising behavior for Indonesian-to-English retrieval.

However, a single successful query is insufficient to establish general multilingual retrieval performance.

### 7.4 Q04 — Concept-Based Query

**Query:** `pain relief medication during pregnancy`

| Rank | Document ID | Medication | Category | Similarity |
|---|---|---|---|---|
| 1 | TGA_01250 | paracetamol | A | 0.6990 |
| 2 | TGA_00711 | flurbiprofen | C | 0.6829 |
| 3 | TGA_01467 | safinamide (as mesilate) | B3 | 0.6725 |
| 4 | TGA_00481 | diazoxide | C | 0.6689 |
| 5 | TGA_01144 | neostigmine | B2 | 0.6609 |

**Observations:**

- Paracetamol was retrieved at rank 1.
- Flurbiprofen was also retrieved.
- Several subsequent results were not clearly related to pain relief.
- The results indicate inconsistent ranking quality for broad concept-based queries.

**Preliminary interpretation:**

The model can retrieve relevant medications from conceptual queries, but ranking quality requires further improvement.

This provides motivation for investigating hybrid retrieval and additional ranking constraints.

## 8. Summary of Results

| Query ID | Expected Target | Top-1 Result | Top-1 Similarity | Initial Assessment |
|---|---|---|---|---|
| Q01 | paracetamol | paracetamol | 0.5675 | Target found |
| Q02 | ibuprofen | ibuprofen | 0.7807 | Target found |
| Q03 | ibuprofen | ibuprofen | 0.8042 | Cross-language target found |
| Q04 | Relevant pain-relief medication | paracetamol | 0.6990 | Relevant initial result |

All four queries returned a relevant or expected document at rank 1 under the initial qualitative assessment.

This observation must not be interpreted as a formal Precision@1 measurement because the experiment has not yet established a predefined relevance annotation protocol.

## 9. Technical Challenges

### 9.1 Python Compatibility

The original Python 3.14 environment encountered dependency resolution problems during the installation of machine learning libraries.

**Resolution:**

A separate Python 3.11 virtual environment was created.

```bash
python3.11 -m venv .venv-ml
source .venv-ml/bin/activate
```

### 9.2 NumPy and PyTorch Incompatibility

The initial environment used NumPy 2.4.6 with PyTorch 2.2.2.

The program produced:

```text
RuntimeError: Numpy is not available
```

**Resolution:**

NumPy was changed to version 1.26.4.

### 9.3 Transformers Compatibility

A newer Transformers installation required a newer PyTorch version than the installed PyTorch 2.2.2.

**Resolution:**

The environment was configured with:

- Transformers 4.41.2
- Sentence-Transformers 3.0.1

### 9.4 Pandas Compatibility

Pandas 3.1.0 required NumPy 2.x, conflicting with the selected NumPy 1.26.4 environment.

**Resolution:**

Pandas was changed to version 2.2.3.

### 9.5 Limited Disk Storage

The available disk space was initially approximately 380 MiB.

The pip cache contained approximately 728.9 MB of cached files.

**Resolution:**

The pip cache was cleared:

```bash
python -m pip cache purge
```

Available disk space increased to approximately 1 GiB.

**Remaining concern:**

Additional disk cleanup is recommended before larger experiments.

## 10. Key Findings

1. The Sentence-BERT implementation successfully processed 1,778 medication records.
2. The model generated 384-dimensional embeddings.
3. Medication-specific queries retrieved the expected medications at rank 1.
4. The Indonesian test query successfully retrieved an English-language medication record.
5. Broad concept-based retrieval produced mixed-quality rankings.
6. Exact medication matching remains important for medication identity resolution.
7. Missing safety statements limit the amount of information available to downstream applications.
8. Semantic similarity does not represent clinical safety, medical correctness, or confidence in a medication recommendation.

## 11. Experiment Limitations

- Only four test queries were evaluated.
- Relevance judgments were qualitative.
- No manually annotated evaluation dataset was used.
- No quantitative comparison against BM25 was performed.
- Precision@K, Recall@K, MRR, and nDCG were not calculated.
- The dataset contains incomplete medication safety information.
- The experiment did not evaluate clinical answer generation.
- Results may vary with model version, preprocessing, and retrieval configuration.

## 12. Next Experiment

**Experiment ID:** EXP-002

**Title:** Hybrid Medication Retrieval Using BM25, Sentence-BERT, and Reciprocal Rank Fusion

**Objectives:**

1. Combine keyword-based and semantic retrieval.
2. Implement Reciprocal Rank Fusion (RRF).
3. Compare retrieved rankings for identical queries.
4. Investigate improvements in medication-specific and concept-based retrieval.
5. Prepare the retrieval pipeline for formal evaluation.

**Planned implementation:**

`src/retrieval/05_hybrid_retrieval.py`

## 13. Conclusion

The initial semantic retrieval experiment was successfully implemented using multilingual Sentence-BERT.

The system retrieved expected medications for exact-name, English-context, and Indonesian cross-language queries.

However, some lower-ranked results were not clearly relevant, particularly for broad concept-based queries.

The findings support further investigation of hybrid retrieval, medication identity matching, and quantitative retrieval evaluation.

The current system is an experimental information retrieval prototype and should not be treated as a validated clinical decision-support system.

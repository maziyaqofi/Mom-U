
# EXP-003: Medication Target Retrieval Evaluation

## 1. Experiment Information

| Field | Description |
|---|---|
| Experiment ID | EXP-003 |
| Project | Mom-U: Pregnancy Medication Information Retrieval |
| Status | Completed — Initial Target Retrieval Evaluation |
| Dataset | TGA Pregnancy Medication Database |
| Corpus Size | 1,778 documents |
| Evaluation Queries | 36 |
| Retrieval Methods | BM25, Sentence-BERT, Hybrid RRF |
| Evaluation Type | Medication-specific target retrieval |

## 2. Objectives

This experiment evaluates the ability of three retrieval methods to identify the intended medication document from user queries.

The objectives are:

1. Measure target retrieval performance using Hit@1, Hit@5, Hit@10, and MRR@10.
2. Compare BM25, Sentence-BERT, and Hybrid RRF.
3. Examine performance across English and Indonesian queries.
4. Identify ranking errors and investigate their causes.
5. Establish a baseline for future retrieval optimization.

This experiment measures medication document identification, not clinical accuracy or medication safety.

## 3. Dataset

The evaluation uses 1,778 medication records from the processed TGA pregnancy medication corpus.

The corpus is stored at:

`data/processed/medication_corpus.jsonl`

Each document contains medication information, including:

- Document ID
- Medication name
- Pregnancy category
- Medication classification
- Safety statement, when available
- Retrieval text

Missing safety statements are treated as missing information, not evidence of medication safety.

Pregnancy categories are not interpreted as ordinal safety scores.

## 4. Evaluation Query Dataset

The evaluation dataset contains 36 queries covering 12 validated medications.

Each medication is represented by three query variants:

| Query Type | Language | Query Count |
|---|---|---:|
| Exact Name | English | 12 |
| English Question | English | 12 |
| Indonesian Question | Indonesian | 12 |
| **Total** | | **36** |

Example query variants:

- `paracetamol`
- `What is the pregnancy safety information for paracetamol?`
- `Apakah paracetamol aman untuk ibu hamil?`

Evaluation files:

- `data/evaluation/evaluation_queries.csv`
- `data/evaluation/relevance_judgments.csv`

The target medication documents were validated against the processed corpus.

The relevance judgment file contains 36 automatically generated seed targets, each assigned a relevance value of 2.

These seed targets do not constitute a complete relevance judgment dataset. Other potentially relevant documents remain unjudged.

## 5. Retrieval Methods

### 5.1 BM25

BM25 is used as a lexical retrieval baseline.

It ranks documents based on token matching and term statistics.

Implementation:

`src/retrieval/01_bm25_baseline.py`

### 5.2 Sentence-BERT

Semantic retrieval uses the pretrained multilingual model:

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

Document embeddings have 384 dimensions.

Semantic similarity is computed using normalized embeddings and dot products.

Implementation:

`src/retrieval/04_semantic_retrieval.py`

### 5.3 Hybrid Retrieval

Hybrid retrieval combines BM25 and Sentence-BERT using Reciprocal Rank Fusion (RRF).

Configuration:

| Parameter | Value |
|---|---|
| BM25 candidate count | 20 |
| Semantic candidate count | 20 |
| RRF constant | 60 |
| Evaluation cutoff | 10 |
| Fusion weighting | Equal |

The RRF score is calculated as:

RRF(d) = sum(1 / (60 + rank_i(d)))

Implementation:

`src/retrieval/05_hybrid_retrieval.py`

No retrieval algorithm modifications were introduced during this evaluation.

## 6. Evaluation Metrics

### 6.1 Hit@1

The proportion of queries whose target document appears at rank 1.

### 6.2 Hit@5

The proportion of queries whose target document appears within the top five results.

### 6.3 Hit@10

The proportion of queries whose target document appears within the top ten results.

### 6.4 MRR@10

Mean Reciprocal Rank at cutoff 10.

For each query, the reciprocal rank is:

- 1 / rank, if the target appears within the top ten.
- 0, otherwise.

MRR@10 is the average reciprocal rank across all queries.

These metrics evaluate retrieval of a predefined target document.

They do not measure the relevance of all retrieved documents.

## 7. Overall Evaluation Results

| Method | Hit@1 | Hit@5 | Hit@10 | MRR@10 |
|---|---:|---:|---:|---:|
| BM25 | 0.8333 | 1.0000 | 1.0000 | 0.9028 |
| Hybrid RRF | **0.8611** | **1.0000** | **1.0000** | **0.9167** |
| Sentence-BERT | 0.5556 | 0.8333 | 0.8611 | 0.6560 |

Hybrid RRF achieved the highest overall Hit@1 and MRR@10.

In terms of first-rank target identification:

- BM25 correctly ranked 30 of 36 targets first.
- Hybrid RRF correctly ranked 31 of 36 targets first.
- Sentence-BERT correctly ranked 20 of 36 targets first.

The Hit@1 improvement of Hybrid over BM25 corresponds to one additional successful query.

Therefore, the observed improvement is modest and should not be interpreted as evidence of general superiority.

## 8. Results by Query Type

### 8.1 Exact Medication Name

| Method | Hit@1 | Hit@5 | MRR@10 |
|---|---:|---:|---:|
| BM25 | 0.8333 | 1.0000 | 0.9028 |
| Hybrid RRF | **0.9167** | **1.0000** | **0.9444** |
| Sentence-BERT | 0.5833 | 0.9167 | 0.7083 |

Hybrid RRF achieved the highest performance for exact medication-name queries.

### 8.2 English Questions

| Method | Hit@1 | Hit@5 | MRR@10 |
|---|---:|---:|---:|
| BM25 | 0.8333 | 1.0000 | 0.9028 |
| Hybrid RRF | 0.8333 | 1.0000 | 0.9028 |
| Sentence-BERT | 0.6667 | 0.9167 | 0.7528 |

BM25 and Hybrid RRF achieved identical aggregate results for English questions.

### 8.3 Indonesian Questions

| Method | Hit@1 | Hit@5 | MRR@10 |
|---|---:|---:|---:|
| BM25 | 0.8333 | 1.0000 | 0.9028 |
| Hybrid RRF | 0.8333 | 1.0000 | 0.9028 |
| Sentence-BERT | 0.4167 | 0.6667 | 0.5069 |

Sentence-BERT performed substantially worse on Indonesian questions than on English questions in this benchmark.

However, all Indonesian queries included medication names that matched the English-language corpus.

The experiment therefore does not isolate cross-lingual semantic understanding.

## 9. Error Analysis

A total of 17 queries had at least one method that failed to place the target document at rank 1.

Three representative cases were investigated.

### 9.1 Case A: Aspirin

Query:

`aspirin`

Target document:

`TGA_00129`

Observed ranking:

| Rank | BM25 | Semantic | Hybrid |
|---|---|---|---|
| 1 | aspirin / dipyridamole | clopidogrel / aspirin | aspirin / dipyridamole |
| 2 | clopidogrel / aspirin | aspirin / dipyridamole | clopidogrel / aspirin |
| 3 | aspirin | aspirin | aspirin |

All three methods placed the standalone aspirin document at rank 3.

The two higher-ranked documents represent combination medications containing aspirin.

The records share the same safety statement in the evaluated corpus.

This case illustrates that the retrieval methods do not explicitly prioritize exact medication-name identity over combination-product matches.

For medication-specific queries, standalone and combination medications should be distinguished.

### 9.2 Case B: Indonesian Loratadine Query

Query:

`Apakah loratadine aman untuk ibu hamil?`

Target document:

`TGA_01000`

Observed target ranks:

| Method | Target Rank |
|---|---:|
| BM25 | 1 |
| Sentence-BERT | Not in Top-10 |
| Hybrid RRF | 2 |

Semantic retrieval ranked leflunomide, flurbiprofen, and teriflunomide among its highest results.

Hybrid RRF placed leflunomide at rank 1 and loratadine at rank 2.

The result demonstrates that semantic similarity alone does not reliably preserve medication identity.

The loratadine record had no available safety statement in the dataset.

Missing safety information must not be interpreted as a safety conclusion.

### 9.3 Case C: English Naproxen Query

Query:

`What is the pregnancy safety information for naproxen?`

Target document:

`TGA_01133`

Observed target ranks:

| Method | Target Rank |
|---|---:|
| BM25 | 1 |
| Sentence-BERT | Not in Top-10 |
| Hybrid RRF | 2 |

Hybrid RRF ranked zonisamide first and naproxen second.

The result shows that rank fusion may promote documents that receive contributions from both candidate lists even when they do not match the medication requested by the user.

RRF combines retrieval ranks; it does not validate medication identity or clinical relevance.

## 10. Key Findings

1. Hybrid RRF achieved the highest overall Hit@1 (0.8611) and MRR@10 (0.9167).
2. BM25 remained competitive, achieving Hit@1 of 0.8333.
3. The overall Hybrid improvement over BM25 was limited to one additional first-rank success.
4. Sentence-BERT performed less effectively for medication-specific target identification.
5. Sentence-BERT showed its lowest performance on Indonesian questions.
6. Exact medication-name matching is important for distinguishing standalone and combination medications.
7. Hybrid RRF can both improve and degrade target rankings.
8. Retrieval scores do not indicate medication safety or clinical confidence.

## 11. Limitations

### 11.1 Small Evaluation Dataset

Only 36 queries were evaluated.

The query set covers 12 medications and three templated query forms.

This limits linguistic diversity and generalizability.

### 11.2 Exact Medication Names

Every query includes the medication name as it appears in the corpus.

The benchmark does not adequately evaluate:

- Misspellings
- Medication synonyms
- Brand names
- Implicit medication references
- General medication-class questions

### 11.3 Incomplete Relevance Judgments

Only one seed target was assigned to each query.

Other documents were not comprehensively annotated.

Therefore, Precision@K, Recall@K, and nDCG@K were not reported.

### 11.4 No Clinical Validation

The evaluation measures document retrieval performance.

It does not establish the clinical correctness, completeness, or safety of medication recommendations.

### 11.5 Limited Statistical Evidence

The benchmark is small and contains three related queries for each medication.

Results should be interpreted descriptively rather than as statistically established performance differences.

## 12. Proposed Next Experiment

### EXP-004: Entity-Aware Hybrid Retrieval

The next experiment will investigate whether explicit medication-entity recognition and reranking improve target retrieval.

Proposed components:

1. Medication-name detection from user queries.
2. Exact-name prioritization.
3. Distinction between standalone and combination medications.
4. Integration with existing BM25 and Sentence-BERT rankings.
5. Comparison against unchanged EXP-003 baselines.

The proposed method should be evaluated using both the existing benchmark and an expanded query set.

Potential additional evaluation categories include misspellings, medication synonyms, and general medication-information queries.

No improvement is assumed before experimental testing.

## 13. Reproducibility

Evaluation dataset generation:

`src/evaluation/01_prepare_evaluation_queries.py`

Target retrieval evaluation:

`src/evaluation/02_evaluate_target_retrieval.py`

Run:

```bash
python src/evaluation/01_prepare_evaluation_queries.py
python src/evaluation/02_evaluate_target_retrieval.py
```

Evaluation outputs:

- `reports/evaluation/target_retrieval_results.csv`
- `reports/evaluation/target_retrieval_summary.csv`
- `reports/evaluation/target_retrieval_by_query_type.csv`

The evaluation uses the existing corpus, retrieval implementations, and cached document embeddings.

## 14. Conclusion

EXP-003 established an initial quantitative baseline for medication-specific retrieval in Mom-U.

Hybrid RRF achieved the highest overall target retrieval performance, but its improvement over BM25 was small.

Error analysis identified three important challenges:

- Standalone versus combination medication matching
- Semantic retrieval failures involving medication identity
- Ranking degradation introduced by reciprocal rank fusion

These findings motivate further investigation of entity-aware retrieval methods.

The results should not be generalized to broader pregnancy-related information retrieval or clinical medication decision-making without additional evaluation.

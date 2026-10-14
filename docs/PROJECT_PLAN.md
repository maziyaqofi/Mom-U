# Mom-U Project Plan

## Problem
Pregnant users often ask everyday questions such as "Why do I feel nauseous in the morning?" but need reliable, easy-to-understand, sourced information.

## Goal
Build and evaluate a retrieval system that ranks English-language pregnancy education documents for natural-language questions.

## MVP requirements
1. User enters an English question.
2. System preprocesses the query appropriately for each retrieval method.
3. BM25 and semantic retrieval rank documents independently.
4. Hybrid retrieval fuses ranks using Reciprocal Rank Fusion.
5. Interface shows titles, snippets, provenance, URLs, and review dates where available.
6. Evaluation reports Precision@5, Recall@5, MRR@10, nDCG@10, and latency.
7. Medical safety: clear educational-only disclaimer, prominent source citations, and emergency guidance for red-flag questions reviewed by a qualified clinician.

## Proposed milestones
- [ ] M1: Approve scope and data sourcing rules.
- [ ] M2: Collect and audit a pilot corpus (20–30 documents).
- [ ] M3: Expand to a target corpus of 100–300 eligible documents, subject to rights and quality.
- [ ] M4: Build BM25 baseline.
- [ ] M5: Build semantic retrieval and hybrid fusion.
- [ ] M6: Create 30–50 test queries and reviewed relevance judgments.
- [ ] M7: Run reproducible evaluation and error analysis.
- [ ] M8: Build Streamlit UI and conduct usability/safety checks.
- [ ] M9: Prepare final report and demo.

## Out of scope for first version
- Diagnosis, medical triage, medication prescriptions, and personalized clinical recommendations.
- Unverified generative medical answers.
- User accounts or storage of personal pregnancy/health information.

## Deliverables
Clean repository, corpus manifest, reproducible retrieval code, qrels, evaluation report, demo app, and final presentation.

# Progress Log

## 2026-10-14 — Initial repository scaffold
- [x] Confirm project name: Mom-U.
- [x] Confirm English as project language.
- [x] Confirm pregnant women as intended users.
- [x] Draft project scope, data collection, evaluation, and decision documents.
- [ ] Create remote GitHub repository and push initial commit.
- [ ] Verify licenses and collect first real pilot documents.
- [ ] Validate corpus schema and build first retrieval baseline.

### Next action
Create the remote GitHub repository, then begin a documented pilot data collection.

## Phase 1: Corpus Preparation

**Date:** October 17, 2026

### Completed
- Prepared a source inventory containing 30 pregnancy-related articles.
- Verified that article URLs are accessible and their content is in English.
- Configured the Python virtual environment.
- Loaded the Excel inventory using pandas.
- Cleaned article metadata and generated consistent document IDs.
- Successfully tested article extraction using requests and trafilatura.
- Extracted a sample NHS article (2,467 characters).
- Created a sample JSONL document.
- Implemented basic corpus validation.

### Current Status
Phase 1C — Corpus Extraction (Pilot Completed)

### Next Steps
- Review source content permissions.
- Automate extraction for eligible articles.
- Validate extracted article content.
- Prepare the complete corpus for information retrieval experiments.

### Planned Retrieval Methods
- BM25
- Sentence-BERT
- Hybrid Retrieval using Reciprocal Rank Fusion (RRF)

### Notes
Full-text article content is stored locally and is excluded from the public repository until redistribution permissions have been verified.
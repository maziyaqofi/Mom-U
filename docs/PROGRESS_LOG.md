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
## Application Development — Backend API and Frontend Preparation

**Date:** November 20, 2026

### Backend Development

**Completed**
- Created the FastAPI application in `app/main.py`.
- Implemented medication API routes in `app/routes/medications.py`.
- Integrated the existing information retrieval modules through `app/services/ir_service.py`.
- Implemented medication query resolution.
- Implemented token-based medication identity verification sessions.
- Implemented user confirmation and verified medication retrieval.
- Added API health-check and root endpoints.
- Verified the API using Swagger UI and HTTP requests.

### Available API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Application information |
| GET | `/health` | Health check |
| POST | `/api/medications/resolve` | Resolve medication queries |
| POST | `/api/medications/verify` | Prepare medication identity verification |
| POST | `/api/medications/confirm` | Confirm selected medication candidates and retrieve records |

### API Testing

- Tested exact medication name matching.
- Tested fuzzy medication name suggestions.
- Tested unresolved medication queries.
- Tested medication identity confirmation.
- Tested invalid and reused verification tokens.
- Tested invalid document IDs and retry behavior.
- Tested queries containing multiple medications.
- Verified retrieval of medication records and their source information.

### Frontend Preparation

**Confirmed Decisions**
- Use Vanilla HTML, CSS, and JavaScript.
- Adopt a Modern Healthcare SaaS visual direction.
- Integrate the frontend with the existing FastAPI backend.
- Preserve existing research and evaluation modules in `src/`.

**Current Status**

Backend API prototype implemented and tested. Frontend implementation not yet started.

### Next Steps
- Create the frontend directory structure.
- Implement the main application layout and design system.
- Build the medication search interface.
- Integrate medication verification and confirmation workflows.
- Display retrieved medication information with source attribution.
- Test frontend and backend integration.

# Dataset Collection Protocol

## Corpus design
Primary corpus: patient-facing pregnancy education materials written in English. Secondary evidence layer: scientific articles and reviews (not directly surfaced as lay guidance without review).

## Candidate sources
1. MedlinePlus health-topic summaries and XML/web service: https://medlineplus.gov/about/developers/webservices/ ; check content reuse guidance https://medlineplus.gov/about/using/usingcontent/ .
2. NHS pregnancy education pages: https://www.nhs.uk/pregnancy/ ; review permissions before reproducing content.
3. PubMed metadata/abstracts via NCBI E-utilities: https://www.ncbi.nlm.nih.gov/home/develop/api/ ; abstract copyright varies.
4. PMC Open Access Subset for licensed scientific full text: https://pmc.ncbi.nlm.nih.gov/tools/openftlist/ ; check each license.

## Collection steps
1. Define topic coverage: symptoms, nutrition, prenatal care, fetal development, screening, complications, mental well-being, and postpartum preparation.
2. Make a source inventory with URL, publisher, date, and content-use permissions.
3. Collect metadata and only text permitted for local reuse; otherwise store metadata, link, and a brief independently written summary where permitted.
4. Record title, text/snippet, topic, source, source URL, content type, date, license, and collection date.
5. Remove duplicates, inspect quality, and flag stale or unclear guidance.
6. Have clinical content and safety notices reviewed by a qualified healthcare professional before public deployment.
7. Split test queries from any tuning queries; annotate document relevance to queries.

## Suggested record fields
`document_id`, `title`, `content`, `topic`, `source_name`, `source_url`, `document_type`, `published_date`, `reviewed_date`, `license`, `collected_at`, `audience`, `clinical_review_status`.

## Rights and privacy
- An accessible webpage is not necessarily reusable under copyright law.
- Never assume PubMed abstracts or all PMC papers are open licensed.
- Respect APIs, robots policies, attribution, and rate limits.
- Do not collect user medical histories or personal identifiers.

## Pilot acceptance criteria
- 20–30 real, verifiable documents with stable URLs and clear reuse status.
- At least five pregnancy topics represented.
- All metadata fields validated; duplicates identified.

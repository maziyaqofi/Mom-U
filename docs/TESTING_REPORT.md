# MOM-U Application Testing Report

## 1. Testing Overview

This document records the functional, API, retrieval, and user interface testing performed on the MOM-U application.

MOM-U is a pregnancy medication information retrieval application that uses a FastAPI backend and a web-based frontend. The application retrieves medication records from the Australian TGA Pregnancy Database and requires user confirmation before displaying selected records.

**Testing date:** 25 November 2026

**Testing scope:**
- Backend API functionality
- Medication entity resolution
- Exact and fuzzy medication matching
- Multiple medication detection and retrieval
- User confirmation workflow
- API input validation and error handling
- Frontend integration
- Desktop and mobile responsiveness

## 2. Testing Environment

| Component | Environment |
|---|---|
| Operating System | macOS |
| Backend | Python / FastAPI |
| Frontend | HTML, CSS, Vanilla JavaScript |
| API Testing | cURL and Python urllib |
| Browser | Google Chrome |
| Local Server | Uvicorn |
| Application URL | http://127.0.0.1:8000 |
| Data Source | Australian TGA Pregnancy Database |

## 3. Functional Testing

The following test cases evaluate the application's main user workflows.

| ID | Test Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC-01 | Search exact medication name: Ibuprofen | Return the matching medication candidate | Ibuprofen was identified and its record was retrieved after confirmation | PASS |
| TC-02 | Search with a misspelled name: Loratadin | Suggest relevant medication candidates | Loratadine, Desloratadine, and Olopatadine were suggested; selected records were retrieved correctly | PASS |
| TC-03 | Search an unknown medication name | No matching candidate or verification session should be returned | No verification session was created and the frontend displayed a no-session message | PASS |
| TC-04 | Search using uppercase input: IBUPROFEN | Resolve the medication regardless of letter case | Ibuprofen was identified and retrieved successfully | PASS |
| TC-05 | Submit empty or whitespace-only input | Prevent invalid search submission | Browser required-field validation and frontend whitespace validation worked | PASS |
| TC-06 | Select one medication candidate | Retrieve only the selected medication record | One selected record was returned | PASS |
| TC-07 | Select multiple medication candidates | Retrieve all selected medication records | Two selected records were returned correctly | PASS |
| TC-08 | Confirm without selecting a candidate | Display a validation message and prevent confirmation | The application displayed a message requesting at least one medication selection | PASS |
| TC-09 | Search typo: paracetmol | Suggest the closest matching medication and require confirmation | Paracetamol was suggested with 95.24% similarity and retrieved after confirmation | PASS |
| TC-10 | Detect multiple medication names in one query | Identify each explicitly mentioned medication | Paracetamol and Ibuprofen were identified with 100% similarity | PASS |
| TC-11 | Confirm multiple medication candidates | Retrieve all user-selected medication records | Paracetamol and Ibuprofen records were both returned successfully | PASS |

## 4. API Validation Testing

These tests evaluate backend input validation and error handling.

| ID | Test Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC-12 | Submit request without the required query field | Return HTTP 422 validation error | HTTP 422 returned with a missing-field validation message | PASS |
| TC-13 | Submit a numeric value instead of a string query | Return HTTP 422 validation error | HTTP 422 returned with a string-type validation message | PASS |
| TC-14 | Submit malformed JSON | Return HTTP 422 JSON parsing error | HTTP 422 returned with a JSON decode error | PASS |
| TC-15 | Check backend and frontend endpoints | All required endpoints should return HTTP 200 | Health endpoint, homepage, JavaScript files, and CSS file returned HTTP 200 | PASS |

### TC-15 Endpoint Details

| Endpoint | Description | HTTP Status |
|---|---|---|
| `/health` | Backend health check | 200 |
| `/` | Frontend homepage | 200 |
| `/js/api.js` | Frontend API script | 200 |
| `/js/app.js` | Frontend application script | 200 |
| `/css/style.css` | Frontend stylesheet | 200 |

## 5. UI/UX and Responsive Testing

### Desktop Interface

The desktop interface was inspected through Google Chrome.

Observed results:
- Header and navigation were displayed correctly.
- Hero section and medication search form were properly aligned.
- Typography, spacing, and color consistency were visually appropriate.
- Main application elements were accessible.

**Result: PASS**

### Mobile Interface

The mobile interface was inspected using Chrome DevTools device emulation.

Initial observation:
- Home and About navigation links were hidden on mobile screens.

Improvement implemented:
- Navigation links remain visible on mobile.
- Navigation spacing and font size were adjusted.
- Medication Information status badge was hidden on mobile to preserve header space.

Follow-up verification:
- Home navigation correctly navigates to the hero section.
- About navigation correctly navigates to the important information section.
- Logo and navigation links remain visible in the mobile header.

**TC-16 — Mobile Navigation: PASS**

## 6. Retrieval and Record Observations

The following observations were obtained during functional testing.

### Fuzzy Matching

For the query `paracetmol`:
- Suggested medication: Paracetamol
- Document ID: `TGA_01250`
- Match type: `fuzzy_suggestion`
- Similarity: 95.24%
- User confirmation was required before retrieval.

### Multiple Medication Detection

For the query:

`Can I take paracetamol and ibuprofen during pregnancy?`

The system identified:
- Paracetamol — `TGA_01250`
- Ibuprofen — `TGA_00831`

Both candidates were explicitly mentioned and had a similarity score of 100%.

After user confirmation, both medication records were successfully retrieved.

### Safety Statement Availability

The retrieved records demonstrated different information availability:

| Medication | Pregnancy Category | Safety Statement |
|---|---|---|
| Paracetamol | A | Not available |
| Ibuprofen | C | Available |

The application represents missing safety statements explicitly. Missing information must not be interpreted as evidence that a medication is safe.

Pregnancy categories and retrieved statements are presented as source information, not as individualized medical recommendations.

## 7. Test Summary

| Testing Area | Test Cases | Result |
|---|---:|---|
| Functional Testing | 11 | 11 PASS |
| API Validation and Smoke Testing | 4 | 4 PASS |
| UI/UX and Responsive Testing | 1 | 1 PASS |
| **Total** | **16** | **16 PASS** |

All 16 recorded test cases passed under the tested conditions.

## 8. Known Limitations

The following limitations remain relevant:

1. Functional testing does not establish clinical accuracy or clinical safety.
2. Retrieval similarity scores are not probabilities of medication safety.
3. Pregnancy categories must not be interpreted as a simple ordinal safety ranking.
4. A missing safety statement does not imply that a medication is safe.
5. Multiple medication retrieval does not establish drug interaction analysis.
6. The application depends on the coverage and quality of its underlying medication database.
7. Verification sessions are stored in memory and are intended for the current prototype implementation. They are not persistent across server restarts or shared across multiple independent workers.
8. Desktop and mobile UI checks were manual visual inspections, not automated cross-browser or device compatibility tests.

## 9. Conclusion

The MOM-U prototype successfully completed the recorded functional, API validation, retrieval workflow, and responsive interface tests.

The application demonstrated its ability to:
- Resolve exact medication names.
- Suggest candidates for misspelled medication names.
- Detect multiple medication entities in a single query.
- Require explicit user confirmation before retrieving selected records.
- Return medication information from the underlying database.
- Handle invalid API payloads through appropriate validation responses.
- Serve the frontend and backend endpoints successfully.
- Display a responsive interface with accessible mobile navigation.

These results support the current functional readiness of the MOM-U prototype for further development and research evaluation.

The results should not be interpreted as clinical validation, proof of medication safety, or evidence of diagnostic capability.

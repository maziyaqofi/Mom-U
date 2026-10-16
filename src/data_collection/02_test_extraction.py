import requests
import trafilatura
import json
from pathlib import Path

# Test article URL from the Mom-U source inventory
url = "https://www.nhs.uk/pregnancy/your-pregnancy-care/12-week-scan/"

# Request the webpage
response = requests.get(
    url,
    timeout=20,
    headers={"User-Agent": "MomU-Research-Prototype/0.1"}
)

# Check the HTTP response
print("HTTP status:", response.status_code)
response.raise_for_status()

# Extract the main article text
article_text = trafilatura.extract(
    response.text,
    include_comments=False,
    include_tables=False
)

# Display extraction results
if article_text:
    print("\nExtraction successful!")
    print("Extracted characters:", len(article_text))
    print("\nText preview:")
    print(article_text[:500])
else:
    print("\nNo article text could be extracted.")

# Create a sample document using article metadata
if article_text:
    document = {
        "document_id": "MOMU_001",
        "title": "12-week scan",
        "category": "Prenatal Care & Screening",
        "source": "NHS",
        "url": url,
        "content": article_text
    }

    # Create the output directory
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save the sample document in JSONL format
    output_path = output_dir / "sample_corpus.jsonl"

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(json.dumps(document, ensure_ascii=False) + "\n")

    print("\nSample document saved successfully!")
    print("Output file:", output_path)
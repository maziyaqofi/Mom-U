import json
import re
import shutil
import tempfile
from pathlib import Path

import requests
from bs4 import BeautifulSoup

CORPUS_PATH = Path("data/processed/pregnancy_corpus.jsonl")

TARGET_IDS = {"MOMU_012", "MOMU_021"}

HEADERS = {
    "User-Agent": "Mom-U-Research/1.0",
    "Accept": "text/html",
}


def extract_summary(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    summary = soup.select_one("#topic-summary")

    if summary is None:
        return None

    # Remove elements that do not belong to the summary.
    for element in summary.select("script, style, nav"):
        element.decompose()

    # Preserve headings, paragraphs, and list items.
    blocks = []

    # Extract structured text while preserving nested list items.
    blocks = []

    for element in summary.find_all(["h2", "h3", "h4", "p", "li"]):
        if element.name != "li" and element.find_parent(
            ["h2", "h3", "h4", "p", "li"]
        ):
            continue

        # Work on a copy to avoid modifying the original HTML tree.
        element_copy = BeautifulSoup(str(element), "html.parser")

        if element.name == "li":
            for nested_list in element_copy.find_all(["ul", "ol"]):
                nested_list.decompose()

        text = element_copy.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text).strip()

        # Remove unnecessary spaces before punctuation.
        text = re.sub(r"\s+([,.!?;:])", r"\1", text)

        if not text:
            continue

        if element.name == "li":
            depth = len(element.find_parents("li"))
            indent = "  " * depth
            blocks.append(f"{indent}- {text}")
        else:
            blocks.append(text)

    return "\n\n".join(blocks) or None



def main():
    if not CORPUS_PATH.exists():
        raise FileNotFoundError(f"Corpus not found: {CORPUS_PATH}")

    records = [
        json.loads(line)
        for line in CORPUS_PATH.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    print("Mom-U MedlinePlus Summary Extraction")

    extracted_summaries = {}

    for record in records:
        document_id = record["document_id"]

        if document_id not in TARGET_IDS:
            continue

        print(f"\nDocument: {document_id}")
        print(f"Title: {record['title']}")

        try:
            summary = extract_summary(record["url"])

            if summary:
                extracted_summaries[document_id] = summary

                print("Extraction: Success")
                print("Characters:", len(summary))
                print("\nExtracted Summary:")
                print("-" * 60)
                print(summary)
                print("-" * 60)
            else:
                print("Extraction: Summary section not found")

        except requests.RequestException as error:
            print("Extraction failed:", error)

    # Update the corpus only if all target documents succeeded.
    if set(extracted_summaries) == TARGET_IDS:
        save_extracted_summaries(extracted_summaries)
    else:
        print("\nCorpus update skipped.")
        print("Both MedlinePlus summaries must be extracted successfully.")


def save_extracted_summaries(extracted_summaries):
    corpus_path = Path("data/processed/pregnancy_corpus.jsonl")
    backup_path = corpus_path.with_suffix(".jsonl.bak")

    if not corpus_path.exists():
        raise FileNotFoundError(f"Corpus not found: {corpus_path}")

    records = []

    with corpus_path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    expected_ids = {"MOMU_012", "MOMU_021"}
    record_ids = [record["document_id"] for record in records]

    if len(records) != 30 or len(record_ids) != len(set(record_ids)):
        raise ValueError("Corpus integrity check failed.")

    if not expected_ids.issubset(record_ids):
        raise ValueError("Required document IDs are missing.")

    if set(extracted_summaries) != expected_ids:
        raise ValueError("Expected summaries for exactly two documents.")

    for record in records:
        document_id = record["document_id"]

        if document_id in extracted_summaries:
            record["content"] = extracted_summaries[document_id]
            record["extraction_status"] = "extracted"

    shutil.copy2(corpus_path, backup_path)

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=corpus_path.parent,
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)

            for record in records:
                temp_file.write(
                    json.dumps(record, ensure_ascii=False) + "\n"
                )

        temp_path.replace(corpus_path)

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    print("\nCorpus updated successfully.")
    print(f"Total documents: {len(records)}")
    print(f"Updated documents: {len(extracted_summaries)}")
    print(f"Backup: {backup_path}")

if __name__ == "__main__":
    main()

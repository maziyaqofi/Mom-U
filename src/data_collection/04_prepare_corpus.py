import json
from pathlib import Path

import pandas as pd

# Define input and output paths
input_path = Path("data/raw/Corpus Mom-U.xlsx")
output_path = Path("data/processed/corpus_inventory.jsonl")

# Load the source inventory
df = pd.read_excel(
    input_path,
    header=1,
    usecols="B:F"
)

# Clean metadata
text_columns = [
    "Article Title",
    "Category",
    "Source",
    "URL"
]

for column in text_columns:
    df[column] = df[column].astype("string").str.strip()

# Create the output directory
output_path.parent.mkdir(parents=True, exist_ok=True)

# Prepare structured documents
documents = []

for _, row in df.iterrows():
    document = {
        "document_id": f"MOMU_{int(row['ID']):03d}",
        "title": row["Article Title"],
        "category": row["Category"],
        "source": row["Source"],
        "url": row["URL"],
        "language": "en",
        "content": None,
        "extraction_status": "pending",
        "usage_permission": "not_verified"
    }

    documents.append(document)

# Save the metadata inventory
with open(output_path, "w", encoding="utf-8") as file:
    for document in documents:
        file.write(
            json.dumps(document, ensure_ascii=False) + "\n"
        )

print("Corpus inventory created successfully!")
print("Total documents:", len(documents))
print("Output file:", output_path)
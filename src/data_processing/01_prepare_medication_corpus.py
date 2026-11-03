
from pathlib import Path
import json
import pandas as pd

# Project directories
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data/raw/medicines-pregnancy-current-database-2026-10-21.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data/processed"
REPORT_DIR = PROJECT_ROOT / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Load the original dataset
df = pd.read_csv(RAW_FILE, dtype=str, keep_default_na=False)

required_columns = [
    "Name",
    "Category",
    "Safety statement",
    "Classification 1",
    "Classification 2",
    "Classification 3",
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

# Normalize whitespace without changing the source file
for column in required_columns:
    df[column] = (
        df[column]
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

# Create a unique identifier for each source row
df.insert(
    0,
    "document_id",
    [f"TGA_{i:05d}" for i in range(1, len(df) + 1)]
)

# Keep both the source name and a normalized search name
df["normalized_name"] = df["Name"].str.casefold()

# Build the retrieval text from available source fields
def build_retrieval_text(row):
    parts = [
        f"Medication: {row['Name']}",
        f"Pregnancy category: {row['Category']}",
    ]

    if row["Safety statement"]:
        parts.append(
            f"Pregnancy safety statement: {row['Safety statement']}"
        )

    for level in range(1, 4):
        value = row[f"Classification {level}"]
        if value:
            parts.append(f"Classification {level}: {value}")

    return "\n".join(parts)


df["retrieval_text"] = df.apply(
    build_retrieval_text,
    axis=1
)

df["has_safety_statement"] = (
    df["Safety statement"] != ""
)

# Export the structured corpus
csv_output = OUTPUT_DIR / "medication_corpus.csv"
jsonl_output = OUTPUT_DIR / "medication_corpus.jsonl"

df.to_csv(csv_output, index=False)

with jsonl_output.open("w", encoding="utf-8") as file:
    for record in df.to_dict(orient="records"):
        file.write(
            json.dumps(record, ensure_ascii=False) + "\n"
        )

# Generate a feasibility report
report = {
    "total_documents": len(df),
    "unique_medication_names": int(df["normalized_name"].nunique()),
    "documents_with_safety_statement": int(
        df["has_safety_statement"].sum()
    ),
    "documents_without_safety_statement": int(
        (~df["has_safety_statement"]).sum()
    ),
    "category_distribution": (
        df["Category"].value_counts().to_dict()
    ),
    "missing_values": {
        col: int((df[col] == "").sum())
        for col in required_columns
    },
}

report_file = REPORT_DIR / "medication_dataset_feasibility.json"

with report_file.open("w", encoding="utf-8") as file:
    json.dump(report, file, indent=2, ensure_ascii=False)

print("Medication corpus preparation completed.")
print(f"Total documents: {len(df)}")
print(f"Unique names: {df['normalized_name'].nunique()}")
print(f"Documents with safety statements: {report['documents_with_safety_statement']}")
print(f"Documents without safety statements: {report['documents_without_safety_statement']}")
print(f"CSV output: {csv_output}")
print(f"JSONL output: {jsonl_output}")
print(f"Report: {report_file}")

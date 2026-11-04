
import csv
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMAGE_DIR = PROJECT_ROOT / "data/ocr_samples"
GROUND_TRUTH_PATH = (
    PROJECT_ROOT / "data/evaluation/ocr_ground_truth.csv"
)

SUPPORTED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"
}

REQUIRED_COLUMNS = {
    "image",
    "expected_medication",
    "expected_document_id",
    "verification_status",
}


def main():
    print("=== EXP-005D OCR Ground Truth Validation ===")

    with GROUND_TRUTH_PATH.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)

        if not REQUIRED_COLUMNS.issubset(reader.fieldnames or []):
            raise ValueError("Missing required ground truth columns.")

        rows = list(reader)

    image_files = {
        path.name
        for path in IMAGE_DIR.iterdir()
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    }

    listed_images = [row["image"].strip() for row in rows]
    counts = Counter(listed_images)

    missing_files = sorted(set(listed_images) - image_files)
    unlisted_files = sorted(image_files - set(listed_images))
    duplicates = sorted(
        name for name, count in counts.items() if count > 1
    )

    verified = sum(
        row["verification_status"].strip().lower() == "verified"
        for row in rows
    )

    incomplete = [
        row["image"]
        for row in rows
        if not row["expected_medication"].strip()
        or not row["expected_document_id"].strip()
    ]

    print(f"Image files: {len(image_files)}")
    print(f"Ground truth rows: {len(rows)}")
    print(f"Verified rows: {verified}")
    print(f"Incomplete target rows: {len(incomplete)}")

    print(f"\nMissing image files: {missing_files}")
    print(f"Unlisted image files: {unlisted_files}")
    print(f"Duplicate image entries: {duplicates}")

    if missing_files or unlisted_files or duplicates:
        print("\nValidation status: FAILED")
    elif incomplete:
        print("\nValidation status: INCOMPLETE")
        print("Manual ground truth verification is required.")
    elif verified != len(rows):
        print("\nValidation status: PENDING VERIFICATION")
    else:
        print("\nValidation status: READY")


if __name__ == "__main__":
    main()

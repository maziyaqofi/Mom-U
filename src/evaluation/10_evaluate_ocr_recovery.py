import csv
import importlib.util
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RETRIEVAL_DIR = PROJECT_ROOT / "src/retrieval"

RECOVERY_PATH = PROJECT_ROOT / "reports/ocr/ocr_recovery_results.csv"
GROUND_TRUTH_PATH = PROJECT_ROOT / "data/evaluation/ocr_ground_truth.csv"
OUTPUT_PATH = PROJECT_ROOT / "reports/evaluation/ocr_recovery_recognition.csv"


def load_module(filename, module_name):
    path = RETRIEVAL_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def main():
    matching = load_module(
        "02_medication_name_matching.py", "matching"
    )
    recognition = load_module(
        "06_medication_entity_recognition.py", "recognition"
    )
    resolver = load_module(
        "08_medication_candidate_resolution.py", "resolver"
    )

    medications = matching.load_medications()

    ground_truth = {
        row["image"]: row["expected_document_id"].strip()
        for row in read_csv(GROUND_TRUTH_PATH)
        if row["verification_status"].strip().lower() == "verified"
    }

    results = []

    for row in read_csv(RECOVERY_PATH):
        image_name = row["image"]

        if image_name not in ground_truth:
            continue

        text = row["extracted_text"]

        if row.get("error", "").strip() or not text.strip():
            status = "unresolved"
            candidates = []
        else:
            resolution = resolver.resolve_medication(
                text, medications, matching, recognition
            )
            status = resolution["status"]
            candidates = (
                resolution["entities"]
                if resolution["entities"]
                else resolution["suggestions"]
            )

        expected_id = ground_truth[image_name]

        hit_at_1 = bool(candidates) and (
            expected_id in candidates[0]["document_ids"]
        )

        hit_at_5 = any(
            expected_id in candidate["document_ids"]
            for candidate in candidates[:5]
        )

        results.append({
            "image": image_name,
            "variant": row["variant"],
            "psm": row["psm"],
            "resolution_status": status,
            "candidate_names": " | ".join(
                candidate["name"] for candidate in candidates
            ),
            "hit_at_1": int(hit_at_1),
            "hit_at_5": int(hit_at_5),
        })

    if not results:
        raise ValueError("No recovery results available.")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    grouped = defaultdict(list)

    for result in results:
        grouped[result["image"]].append(result)

    print("=== EXP-005G OCR Recovery Recognition ===")

    for image_name, records in sorted(grouped.items()):
        successful = [
            record for record in records
            if record["hit_at_1"] == 1
        ]

        print(f"\nImage: {image_name}")
        print(f"Configurations tested: {len(records)}")
        print(f"Successful Hit@1 configurations: {len(successful)}")

        for record in successful:
            print(
                f"  {record['variant']} | PSM {record['psm']} "
                f"| {record['candidate_names']}"
            )

    print(f"\nResults saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

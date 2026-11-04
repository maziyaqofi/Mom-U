
import csv
import importlib.util
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RETRIEVAL_DIR = PROJECT_ROOT / "src/retrieval"

OCR_RESULTS_PATH = (
    PROJECT_ROOT / "reports/ocr/batch_ocr_results.csv"
)
GROUND_TRUTH_PATH = (
    PROJECT_ROOT / "data/evaluation/ocr_ground_truth.csv"
)
OUTPUT_PATH = (
    PROJECT_ROOT / "reports/evaluation/ocr_recognition_results.csv"
)


def load_module(filename, module_name):
    """Load an existing retrieval module."""
    module_path = RETRIEVAL_DIR / filename

    spec = importlib.util.spec_from_file_location(
        module_name, module_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def read_csv(path):
    """Read CSV records."""
    with path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        return list(csv.DictReader(file))


def evaluate():
    matching = load_module(
        "02_medication_name_matching.py",
        "medication_matching",
    )
    recognition = load_module(
        "06_medication_entity_recognition.py",
        "medication_recognition",
    )
    resolver = load_module(
        "08_medication_candidate_resolution.py",
        "medication_resolver",
    )

    medications = matching.load_medications()

    ground_truth_rows = read_csv(GROUND_TRUTH_PATH)
    ocr_rows = read_csv(OCR_RESULTS_PATH)

    ground_truth = {}

    for row in ground_truth_rows:
        if row["verification_status"].strip().lower() != "verified":
            continue

        ground_truth[row["image"]] = {
            "medication": matching.normalize_name(
                row["expected_medication"]
            ),
            "document_id": row["expected_document_id"].strip(),
        }

    if not ground_truth:
        raise ValueError(
            "No verified ground truth records available."
        )

    results = []

    for row in ocr_rows:
        image_name = row["image"]

        if image_name not in ground_truth:
            continue

        expected = ground_truth[image_name]
        extracted_text = row["extracted_text"]

        if row.get("error", "").strip():
            status = "ocr_error"
            candidates = []
        elif not extracted_text.strip():
            status = "no_text"
            candidates = []
        else:
            resolution = resolver.resolve_medication(
                extracted_text,
                medications,
                matching,
                recognition,
            )

            status = resolution["status"]

            if resolution["entities"]:
                candidates = resolution["entities"]
            else:
                candidates = resolution["suggestions"]

        candidate_ids = [
            document_id
            for candidate in candidates
            for document_id in candidate["document_ids"]
        ]

        expected_id = expected["document_id"]

        hit_at_1 = (
            bool(candidates)
            and expected_id in candidates[0]["document_ids"]
        )
        hit_at_5 = any(
            expected_id in candidate["document_ids"]
            for candidate in candidates[:5]
        )

        results.append({
            "image": image_name,
            "variant": row["variant"],
            "psm": row["psm"],
            "expected_medication": expected["medication"],
            "expected_document_id": expected_id,
            "resolution_status": status,
            "candidate_names": " | ".join(
                candidate["name"] for candidate in candidates
            ),
            "hit_at_1": int(hit_at_1),
            "hit_at_5": int(hit_at_5),
        })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys()),
        )
        writer.writeheader()
        writer.writerows(results)

    grouped = defaultdict(list)

    for result in results:
        key = (result["variant"], result["psm"])
        grouped[key].append(result)

    print("=== EXP-005E OCR Medication Recognition ===")
    print(f"Verified images: {len(ground_truth)}")
    print(f"Evaluations: {len(results)}")

    for (variant, psm), records in sorted(grouped.items()):
        count = len(records)

        hit_1 = sum(r["hit_at_1"] for r in records)
        hit_5 = sum(r["hit_at_5"] for r in records)

        unresolved = sum(
            r["resolution_status"] in {
                "unresolved", "no_text", "ocr_error"
            }
            for r in records
        )

        print(f"\nConfiguration: {variant} | PSM {psm}")
        print(f"Hit@1: {hit_1}/{count} ({hit_1/count:.2%})")
        print(f"Hit@5: {hit_5}/{count} ({hit_5/count:.2%})")
        print(
            f"Unresolved rate: "
            f"{unresolved}/{count} ({unresolved/count:.2%})"
        )

    print(f"\nResults saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    evaluate()


import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CANDIDATES_PATH = (
    PROJECT_ROOT
    / "reports/ocr/automatic_multi_pass_candidates.csv"
)

GROUND_TRUTH_PATH = (
    PROJECT_ROOT
    / "data/evaluation/ocr_ground_truth.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "reports/evaluation"

IMAGE_RESULTS_PATH = (
    OUTPUT_DIR / "automatic_multi_pass_evaluation.csv"
)

SUMMARY_PATH = (
    OUTPUT_DIR / "automatic_multi_pass_summary.csv"
)


def read_csv(path):
    """Read CSV records."""
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def save_csv(path, rows, fieldnames):
    """Save evaluation results to CSV."""
    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(rows)


def get_document_ids(candidate):
    """Extract document IDs from a candidate record."""
    return {
        document_id.strip()
        for document_id in candidate["document_ids"].split(";")
        if document_id.strip()
    }


def evaluate():
    ground_truth_rows = read_csv(GROUND_TRUTH_PATH)
    candidate_rows = read_csv(CANDIDATES_PATH)

    ground_truth = {
        row["image"]: {
            "medication": row["expected_medication"].strip().casefold(),
            "document_id": row["expected_document_id"].strip(),
        }
        for row in ground_truth_rows
        if row["verification_status"].strip().lower() == "verified"
    }

    if not ground_truth:
        raise ValueError("No verified ground truth records found.")

    candidates_by_image = {
        image_name: []
        for image_name in ground_truth
    }

    for row in candidate_rows:
        image_name = row["image"]

        if image_name not in ground_truth:
            raise ValueError(
                f"Candidate image missing from ground truth: {image_name}"
            )

        candidates_by_image[image_name].append(row)

    image_results = []

    total_candidates = 0
    correct_candidates = 0
    false_candidates = 0

    hit_at_1_count = 0
    hit_at_5_count = 0
    false_candidate_images = 0
    unresolved_images = 0
    missed_images = 0
    explicit_recognition_images = 0

    for image_name, expected in sorted(ground_truth.items()):
        candidates = candidates_by_image[image_name]
        expected_id = expected["document_id"]

        candidate_checks = []

        for candidate in candidates:
            candidate_ids = get_document_ids(candidate)
            is_correct = expected_id in candidate_ids

            candidate_checks.append({
                "candidate": candidate,
                "is_correct": is_correct,
            })

            total_candidates += 1

            if is_correct:
                correct_candidates += 1
            else:
                false_candidates += 1

        correct_found = any(
            item["is_correct"]
            for item in candidate_checks
        )

        hit_at_1 = (
            bool(candidate_checks)
            and candidate_checks[0]["is_correct"]
        )

        hit_at_5 = any(
            item["is_correct"]
            for item in candidate_checks[:5]
        )

        has_false_candidate = any(
            not item["is_correct"]
            for item in candidate_checks
        )

        has_explicit_correct = any(
            item["is_correct"]
            and item["candidate"]["match_type"] == "explicit_mention"
            for item in candidate_checks
        )

        unresolved = len(candidates) == 0
        missed = not correct_found

        if hit_at_1:
            hit_at_1_count += 1

        if hit_at_5:
            hit_at_5_count += 1

        if has_false_candidate:
            false_candidate_images += 1

        if unresolved:
            unresolved_images += 1

        if missed:
            missed_images += 1

        if has_explicit_correct:
            explicit_recognition_images += 1

        image_results.append({
            "image": image_name,
            "expected_medication": expected["medication"],
            "expected_document_id": expected_id,
            "candidate_count": len(candidates),
            "candidate_names": " | ".join(
                candidate["medication_name"]
                for candidate in candidates
            ),
            "hit_at_1": int(hit_at_1),
            "hit_at_5": int(hit_at_5),
            "correct_candidate_count": sum(
                item["is_correct"]
                for item in candidate_checks
            ),
            "false_candidate_count": sum(
                not item["is_correct"]
                for item in candidate_checks
            ),
            "has_false_candidate": int(has_false_candidate),
            "has_explicit_correct": int(has_explicit_correct),
            "unresolved": int(unresolved),
            "missed": int(missed),
        })

    total_images = len(ground_truth)

    if not total_images:
        raise ValueError("No images available for evaluation.")

    metrics = [
        {
            "metric": "Hit@1",
            "numerator": hit_at_1_count,
            "denominator": total_images,
        },
        {
            "metric": "Hit@5",
            "numerator": hit_at_5_count,
            "denominator": total_images,
        },
        {
            "metric": "Candidate Precision",
            "numerator": correct_candidates,
            "denominator": total_candidates,
        },
        {
            "metric": "False Candidate Rate",
            "numerator": false_candidate_images,
            "denominator": total_images,
        },
        {
            "metric": "Unresolved Rate",
            "numerator": unresolved_images,
            "denominator": total_images,
        },
        {
            "metric": "Missed Rate",
            "numerator": missed_images,
            "denominator": total_images,
        },
        {
            "metric": "Explicit Recognition Rate",
            "numerator": explicit_recognition_images,
            "denominator": total_images,
        },
    ]

    summary_results = []

    for metric in metrics:
        numerator = metric["numerator"]
        denominator = metric["denominator"]

        percentage = (
            numerator / denominator * 100
            if denominator
            else 0.0
        )

        summary_results.append({
            "metric": metric["metric"],
            "numerator": numerator,
            "denominator": denominator,
            "percentage": round(percentage, 2),
        })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    save_csv(
        IMAGE_RESULTS_PATH,
        image_results,
        list(image_results[0].keys()),
    )

    save_csv(
        SUMMARY_PATH,
        summary_results,
        ["metric", "numerator", "denominator", "percentage"],
    )

    print("=== EXP-005H Evaluation Results ===")
    print(f"Verified images: {total_images}")
    print(f"Total candidates: {total_candidates}")
    print(f"Correct candidates: {correct_candidates}")
    print(f"False candidates: {false_candidates}")

    for metric in summary_results:
        print(
            f"{metric['metric']}: "
            f"{metric['numerator']}/{metric['denominator']} "
            f"({metric['percentage']:.2f}%)"
        )

    print("\n=== Per-Image Results ===")

    for result in image_results:
        print(
            f"{result['image']} | "
            f"Hit@1: {result['hit_at_1']} | "
            f"Hit@5: {result['hit_at_5']} | "
            f"Candidates: {result['candidate_count']} | "
            f"False: {result['false_candidate_count']}"
        )

    print("\n=== Output Files ===")
    print(f"Per-image results: {IMAGE_RESULTS_PATH}")
    print(f"Summary results: {SUMMARY_PATH}")


if __name__ == "__main__":
    evaluate()

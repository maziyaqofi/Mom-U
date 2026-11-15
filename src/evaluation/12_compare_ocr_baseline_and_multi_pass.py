
import csv
import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RETRIEVAL_DIR = PROJECT_ROOT / "src/retrieval"

BASELINE_PATH = PROJECT_ROOT / "reports/ocr/batch_ocr_results.csv"
MULTI_PASS_PATH = (
    PROJECT_ROOT / "reports/ocr/automatic_multi_pass_candidates.csv"
)
GROUND_TRUTH_PATH = (
    PROJECT_ROOT / "data/evaluation/ocr_ground_truth.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "reports/evaluation"
IMAGE_OUTPUT = OUTPUT_DIR / "baseline_vs_multi_pass_per_image.csv"
SUMMARY_OUTPUT = OUTPUT_DIR / "baseline_vs_multi_pass_summary.csv"


def load_module(filename, module_name):
    """Load an existing retrieval module."""
    path = RETRIEVAL_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module: {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_csv(path):
    """Read CSV records."""
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def save_csv(path, rows, fieldnames):
    """Save records to CSV."""
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def resolve_candidates(text, medications, matching, recognition, resolver):
    """Resolve medication candidates from one OCR result."""
    if not text.strip():
        return []

    resolution = resolver.resolve_medication(
        text,
        medications,
        matching,
        recognition,
    )

    candidates = []

    for entity in resolution.get("entities", []):
        candidates.append({
            "name": entity["name"],
            "document_ids": entity.get("document_ids", []),
            "match_type": "explicit_mention",
            "similarity": entity.get("similarity", 100.0),
        })

    for suggestion in resolution.get("suggestions", []):
        candidates.append({
            "name": suggestion["name"],
            "document_ids": suggestion.get("document_ids", []),
            "match_type": "fuzzy_suggestion",
            "similarity": suggestion.get("similarity", 0.0),
        })

    return candidates


def aggregate_candidates(pass_results):
    """Apply the same aggregation rules used in EXP-005H."""
    aggregated = {}

    for result in pass_results:
        for candidate in result["candidates"]:
            key = candidate["name"].casefold().strip()

            if not key:
                continue

            if key not in aggregated:
                aggregated[key] = {
                    "medication_name": candidate["name"],
                    "document_ids": set(),
                    "match_types": set(),
                    "passes": set(),
                    "similarities": [],
                }

            item = aggregated[key]
            item["document_ids"].update(candidate["document_ids"])
            item["match_types"].add(candidate["match_type"])
            item["passes"].add(result["variant"])
            item["similarities"].append(candidate["similarity"])

    output = []

    for item in aggregated.values():
        match_types = item["match_types"]

        primary_match_type = (
            "explicit_mention"
            if "explicit_mention" in match_types
            else "fuzzy_suggestion"
        )

        output.append({
            "medication_name": item["medication_name"],
            "document_ids": ";".join(sorted(item["document_ids"])),
            "match_type": primary_match_type,
            "all_match_types": ";".join(sorted(match_types)),
            "supporting_passes": ";".join(sorted(item["passes"])),
            "pass_count": len(item["passes"]),
            "max_similarity": max(item["similarities"]),
        })

    output.sort(
        key=lambda item: (
            item["match_type"] != "explicit_mention",
            -item["pass_count"],
            -item["max_similarity"],
            item["medication_name"],
        )
    )

    return output


def get_document_ids(candidate):
    """Extract document IDs from a candidate."""
    return {
        value.strip()
        for value in candidate["document_ids"].split(";")
        if value.strip()
    }


def evaluate_method(method_name, candidates_by_image, ground_truth):
    """Calculate metrics using the same rules for each method."""
    image_results = []

    total_candidates = 0
    correct_candidates = 0
    false_candidates = 0

    hit_at_1_count = 0
    hit_at_5_count = 0
    false_candidate_images = 0
    unresolved_images = 0
    missed_images = 0
    explicit_correct_images = 0

    for image_name, expected in sorted(ground_truth.items()):
        candidates = candidates_by_image.get(image_name, [])
        expected_id = expected["document_id"]

        checks = [
            {
                "candidate": candidate,
                "correct": expected_id in get_document_ids(candidate),
            }
            for candidate in candidates
        ]

        correct_count = sum(item["correct"] for item in checks)
        false_count = len(checks) - correct_count

        hit_at_1 = bool(checks) and checks[0]["correct"]
        hit_at_5 = any(item["correct"] for item in checks[:5])

        has_false = false_count > 0
        unresolved = len(candidates) == 0
        missed = correct_count == 0

        explicit_correct = any(
            item["correct"]
            and item["candidate"]["match_type"] == "explicit_mention"
            for item in checks
        )

        total_candidates += len(candidates)
        correct_candidates += correct_count
        false_candidates += false_count

        hit_at_1_count += int(hit_at_1)
        hit_at_5_count += int(hit_at_5)
        false_candidate_images += int(has_false)
        unresolved_images += int(unresolved)
        missed_images += int(missed)
        explicit_correct_images += int(explicit_correct)

        image_results.append({
            "method": method_name,
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
            "correct_candidate_count": correct_count,
            "false_candidate_count": false_count,
            "has_false_candidate": int(has_false),
            "explicit_correct": int(explicit_correct),
            "unresolved": int(unresolved),
            "missed": int(missed),
        })

    total_images = len(ground_truth)

    metrics = [
        ("Hit@1", hit_at_1_count, total_images),
        ("Hit@5", hit_at_5_count, total_images),
        ("Candidate Precision", correct_candidates, total_candidates),
        ("False Candidate Rate", false_candidate_images, total_images),
        ("Unresolved Rate", unresolved_images, total_images),
        ("Missed Rate", missed_images, total_images),
        ("Explicit Recognition Rate", explicit_correct_images, total_images),
    ]

    summary = []

    for metric, numerator, denominator in metrics:
        percentage = (
            numerator / denominator * 100
            if denominator
            else 0.0
        )

        summary.append({
            "method": method_name,
            "metric": metric,
            "numerator": numerator,
            "denominator": denominator,
            "percentage": round(percentage, 2),
        })

    return image_results, summary


def main():
    matching = load_module(
        "02_medication_name_matching.py",
        "comparison_matching",
    )
    recognition = load_module(
        "06_medication_entity_recognition.py",
        "comparison_recognition",
    )
    resolver = load_module(
        "08_medication_candidate_resolution.py",
        "comparison_resolver",
    )

    medications = matching.load_medications()

    ground_truth = {
        row["image"]: {
            "medication": matching.normalize_name(
                row["expected_medication"]
            ),
            "document_id": row["expected_document_id"].strip(),
        }
        for row in read_csv(GROUND_TRUTH_PATH)
        if row["verification_status"].strip().lower() == "verified"
    }

    if not ground_truth:
        raise ValueError("No verified ground truth records found.")

    # Build baseline candidates using the same resolver and
    # aggregation procedure as EXP-005H.
    baseline_passes = {
        image_name: []
        for image_name in ground_truth
    }

    for row in read_csv(BASELINE_PATH):
        image_name = row["image"]

        if image_name not in ground_truth:
            continue

        candidates = resolve_candidates(
            row["extracted_text"],
            medications,
            matching,
            recognition,
            resolver,
        )

        baseline_passes[image_name].append({
            "variant": f"{row['variant']}_psm_{row['psm']}",
            "candidates": candidates,
        })

    baseline_candidates = {
        image_name: aggregate_candidates(pass_results)
        for image_name, pass_results in baseline_passes.items()
    }

    # Load the already aggregated EXP-005H candidates.
    multi_pass_candidates = {
        image_name: []
        for image_name in ground_truth
    }

    for row in read_csv(MULTI_PASS_PATH):
        image_name = row["image"]

        if image_name not in ground_truth:
            continue

        multi_pass_candidates[image_name].append({
            "medication_name": row["medication_name"],
            "document_ids": row["document_ids"],
            "match_type": row["match_type"],
            "all_match_types": row["all_match_types"],
            "supporting_passes": row["supporting_passes"],
            "pass_count": int(row["pass_count"]),
            "max_similarity": float(row["max_similarity"]),
        })

    baseline_images, baseline_summary = evaluate_method(
        "Baseline Aggregation",
        baseline_candidates,
        ground_truth,
    )

    multi_images, multi_summary = evaluate_method(
        "EXP-005H Multi-Pass",
        multi_pass_candidates,
        ground_truth,
    )

    image_results = baseline_images + multi_images
    summary_results = baseline_summary + multi_summary

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    save_csv(
        IMAGE_OUTPUT,
        image_results,
        list(image_results[0].keys()),
    )

    save_csv(
        SUMMARY_OUTPUT,
        summary_results,
        list(summary_results[0].keys()),
    )

    print("=== Baseline vs EXP-005H Comparison ===")
    print(f"Verified images: {len(ground_truth)}")

    for method in ["Baseline Aggregation", "EXP-005H Multi-Pass"]:
        print(f"\n{method}")

        for result in summary_results:
            if result["method"] != method:
                continue

            print(
                f"{result['metric']}: "
                f"{result['numerator']}/{result['denominator']} "
                f"({result['percentage']:.2f}%)"
            )

    print("\n=== Per-Image Comparison ===")

    for image_name in sorted(ground_truth):
        baseline = next(
            row for row in baseline_images
            if row["image"] == image_name
        )
        multi = next(
            row for row in multi_images
            if row["image"] == image_name
        )

        print(f"\n{image_name}")
        print(
            f"Baseline: Hit@1={baseline['hit_at_1']} | "
            f"Candidates={baseline['candidate_names'] or 'None'}"
        )
        print(
            f"EXP-005H: Hit@1={multi['hit_at_1']} | "
            f"Candidates={multi['candidate_names'] or 'None'}"
        )

    print("\n=== Output Files ===")
    print(f"Per-image comparison: {IMAGE_OUTPUT}")
    print(f"Summary comparison: {SUMMARY_OUTPUT}")


if __name__ == "__main__":
    main()

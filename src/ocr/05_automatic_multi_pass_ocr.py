
import csv
import importlib.util
import time
from collections import defaultdict
from pathlib import Path

import pytesseract
from PIL import Image, ImageOps, UnidentifiedImageError


PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMAGE_DIR = PROJECT_ROOT / "data/ocr_samples"
OUTPUT_DIR = PROJECT_ROOT / "reports/ocr"

MATCHING_SCRIPT = (
    PROJECT_ROOT / "src/retrieval/02_medication_name_matching.py"
)
RECOGNITION_SCRIPT = (
    PROJECT_ROOT / "src/retrieval/06_medication_entity_recognition.py"
)
RESOLUTION_SCRIPT = (
    PROJECT_ROOT / "src/retrieval/08_medication_candidate_resolution.py"
)

SUPPORTED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"
}

# Predefined configurations for automatic multi-pass OCR.
CONFIGURATIONS = [
    ("original", 6),
    ("grayscale", 11),
    ("center_crop_upscaled", 6),
    ("rotation_15", 6),
]


def load_module(script_path, module_name):
    """Load an existing project module."""
    spec = importlib.util.spec_from_file_location(
        module_name,
        script_path,
    )

    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module: {script_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def resize_image(image, scale=3):
    """Enlarge an image while preserving its aspect ratio."""
    return image.resize(
        (image.width * scale, image.height * scale),
        Image.Resampling.LANCZOS,
    )


def center_crop(image, fraction=0.75):
    """Crop the central area of an image."""
    width, height = image.size

    new_width = int(width * fraction)
    new_height = int(height * fraction)

    left = (width - new_width) // 2
    top = (height - new_height) // 2

    return image.crop(
        (left, top, left + new_width, top + new_height)
    )


def preprocess_image(image, variant):
    """Apply a predefined preprocessing configuration."""
    if variant == "original":
        return image.copy()

    if variant == "grayscale":
        return ImageOps.grayscale(image)

    if variant == "center_crop_upscaled":
        cropped = center_crop(image)
        return resize_image(cropped)

    if variant == "rotation_15":
        return image.rotate(
            15,
            expand=True,
            fillcolor="white",
        )

    raise ValueError(f"Unknown preprocessing variant: {variant}")


def extract_ocr(image, psm):
    """Extract text using Tesseract OCR."""
    return pytesseract.image_to_string(
        image,
        lang="eng",
        config=f"--psm {psm}",
    ).strip()


def resolve_ocr_candidates(
    text,
    medications,
    matching,
    recognition,
    resolver,
):
    """Resolve medication candidates from OCR text."""
    if not text:
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
    """Aggregate candidates while preserving their OCR provenance."""
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

            item["document_ids"].update(
                candidate["document_ids"]
            )
            item["match_types"].add(candidate["match_type"])
            item["passes"].add(result["variant"])
            item["similarities"].append(
                candidate["similarity"]
            )

    output = []

    for item in aggregated.values():
        match_types = item["match_types"]

        # Explicit recognition is stronger evidence than a fuzzy
        # suggestion, but still requires user confirmation.
        if "explicit_mention" in match_types:
            primary_match_type = "explicit_mention"
        else:
            primary_match_type = "fuzzy_suggestion"

        output.append({
            "medication_name": item["medication_name"],
            "document_ids": ";".join(
                sorted(item["document_ids"])
            ),
            "match_type": primary_match_type,
            "all_match_types": ";".join(sorted(match_types)),
            "supporting_passes": ";".join(sorted(item["passes"])),
            "pass_count": len(item["passes"]),
            "max_similarity": max(item["similarities"]),
            "requires_user_confirmation": True,
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


def save_csv(output_path, rows, fieldnames):
    """Save experiment results to CSV."""
    with output_path.open(
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


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    matching = load_module(
        MATCHING_SCRIPT,
        "medication_name_matching",
    )
    recognition = load_module(
        RECOGNITION_SCRIPT,
        "medication_entity_recognition",
    )
    resolver = load_module(
        RESOLUTION_SCRIPT,
        "medication_candidate_resolution",
    )

    medications = matching.load_medications()

    image_paths = sorted(
        path for path in IMAGE_DIR.iterdir()
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not image_paths:
        raise FileNotFoundError(
            f"No supported images found in {IMAGE_DIR}"
        )

    pass_results = []
    candidate_results = []

    total_start = time.perf_counter()

    print("=== EXP-005H Automatic Multi-Pass OCR ===")
    print(f"Images found: {len(image_paths)}")
    print(f"Medication corpus: {len(medications)}")
    print(f"Configurations per image: {len(CONFIGURATIONS)}")

    for image_path in image_paths:
        print(f"\nImage: {image_path.name}")

        try:
            with Image.open(image_path) as source:
                original_image = (
                    ImageOps.exif_transpose(source).convert("RGB")
                )

        except (OSError, UnidentifiedImageError) as error:
            print(f"Image error: {error}")

            for variant, psm in CONFIGURATIONS:
                pass_results.append({
                    "image": image_path.name,
                    "variant": variant,
                    "psm": psm,
                    "extracted_text": "",
                    "text_detected": False,
                    "character_count": 0,
                    "processing_time_seconds": 0.0,
                    "error": str(error),
                })

            continue

        image_candidates = []

        for variant, psm in CONFIGURATIONS:
            start_time = time.perf_counter()

            try:
                processed_image = preprocess_image(
                    original_image,
                    variant,
                )

                text = extract_ocr(processed_image, psm)

                candidates = resolve_ocr_candidates(
                    text,
                    medications,
                    matching,
                    recognition,
                    resolver,
                )

                error = ""

            except (
                OSError,
                ValueError,
                pytesseract.TesseractError,
            ) as exception:
                text = ""
                candidates = []
                error = str(exception)

            processing_time = (
                time.perf_counter() - start_time
            )

            pass_results.append({
                "image": image_path.name,
                "variant": variant,
                "psm": psm,
                "extracted_text": text,
                "text_detected": bool(text),
                "character_count": len(text),
                "processing_time_seconds": round(
                    processing_time, 4
                ),
                "error": error,
            })

            image_candidates.append({
                "variant": variant,
                "candidates": candidates,
            })

            preview = " ".join(text.split())[:120]

            print(
                f"{variant} | PSM {psm} | "
                f"{preview or 'No text detected'}"
            )

            if error:
                print(f"OCR error: {error}")

        aggregated = aggregate_candidates(image_candidates)

        for candidate in aggregated:
            candidate_results.append({
                "image": image_path.name,
                **candidate,
            })

        print(f"Aggregated candidates: {len(aggregated)}")

        for candidate in aggregated:
            print(
                f"  - {candidate['medication_name']} "
                f"| {candidate['match_type']} "
                f"| Passes: {candidate['pass_count']}"
            )

    total_time = time.perf_counter() - total_start

    pass_output = OUTPUT_DIR / (
        "automatic_multi_pass_results.csv"
    )
    candidate_output = OUTPUT_DIR / (
        "automatic_multi_pass_candidates.csv"
    )

    if not pass_results:
        raise ValueError("No OCR results were generated.")

    save_csv(
        pass_output,
        pass_results,
        list(pass_results[0].keys()),
    )

    candidate_fields = [
        "image",
        "medication_name",
        "document_ids",
        "match_type",
        "all_match_types",
        "supporting_passes",
        "pass_count",
        "max_similarity",
        "requires_user_confirmation",
    ]

    save_csv(
        candidate_output,
        candidate_results,
        candidate_fields,
    )

    successful_passes = sum(
        bool(result["text_detected"])
        for result in pass_results
    )

    print("\n=== EXP-005H Summary ===")
    print(f"Images processed: {len(image_paths)}")
    print(f"Total OCR evaluations: {len(pass_results)}")
    print(f"Passes with detected text: {successful_passes}")
    print(f"Aggregated candidates: {len(candidate_results)}")
    print(f"Total processing time: {total_time:.2f} seconds")
    print(f"OCR results saved to: {pass_output}")
    print(f"Candidate results saved to: {candidate_output}")


if __name__ == "__main__":
    main()

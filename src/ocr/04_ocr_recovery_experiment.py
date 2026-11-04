
import csv
from pathlib import Path

import pytesseract
from PIL import Image, ImageOps, ImageEnhance


PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMAGE_DIR = PROJECT_ROOT / "data/ocr_samples"
OUTPUT_DIR = PROJECT_ROOT / "reports/ocr"

TARGET_IMAGES = [
    "medication_02.jpg",
    "medication_07.jpg",
    "medication_08.webp",
]

PSM_MODES = [6, 11]


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


def create_variants(image):
    """Generate preprocessing variants for OCR recovery."""
    grayscale = ImageOps.grayscale(image)
    enhanced = ImageEnhance.Contrast(grayscale).enhance(2.0)

    variants = {
        "original": image,
        "upscaled_3x": resize_image(image),
        "grayscale_upscaled_3x": resize_image(grayscale),
        "enhanced_upscaled_3x": resize_image(enhanced),
        "center_crop_upscaled": resize_image(
            center_crop(image)
        ),
    }

    for angle in [-45, -30, -15, 15, 30, 45, 90]:
        rotated = image.rotate(
            angle,
            expand=True,
            fillcolor="white",
        )

        variants[f"rotation_{angle}"] = rotated

    return variants


def run_experiment():
    """Evaluate OCR recovery configurations."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    print("=== EXP-005F OCR Recovery Experiment ===")

    for filename in TARGET_IMAGES:
        image_path = IMAGE_DIR / filename

        if not image_path.is_file():
            print(f"Image not found: {filename}")
            continue

        with Image.open(image_path) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")

        variants = create_variants(image)

        print(f"\nImage: {filename}")
        print(f"Variants: {len(variants)}")

        for variant_name, processed_image in variants.items():
            for psm in PSM_MODES:
                try:
                    text = pytesseract.image_to_string(
                        processed_image,
                        lang="eng",
                        config=f"--psm {psm}",
                    ).strip()

                    error = ""

                except pytesseract.TesseractError as exc:
                    text = ""
                    error = str(exc)

                results.append({
                    "image": filename,
                    "variant": variant_name,
                    "psm": psm,
                    "extracted_text": text,
                    "text_detected": bool(text),
                    "character_count": len(text),
                    "error": error,
                })

                preview = " ".join(text.split())[:120]

                print(
                    f"{variant_name} | PSM {psm} | "
                    f"{preview or 'No text detected'}"
                )

    if not results:
        raise ValueError("No OCR results were generated.")

    output_path = OUTPUT_DIR / "ocr_recovery_results.csv"

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys()),
        )
        writer.writeheader()
        writer.writerows(results)

    print("\n=== Summary ===")
    print(f"Target images: {len(TARGET_IMAGES)}")
    print(f"Total configurations evaluated: {len(results)}")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    run_experiment()

import argparse
import csv
from pathlib import Path

import pytesseract
from PIL import Image, ImageEnhance, ImageOps


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "reports/ocr"
PSM_MODES = [3, 6, 11]


def prepare_images(image_path):
    """Create image variants for OCR comparison."""
    with Image.open(image_path) as source:
        original = ImageOps.exif_transpose(source).convert("RGB")

    grayscale = ImageOps.grayscale(original)

    enlarged = grayscale.resize(
        (grayscale.width * 2, grayscale.height * 2),
        Image.Resampling.LANCZOS,
    )

    enhanced = ImageEnhance.Contrast(enlarged).enhance(2.0)
    enhanced = ImageOps.autocontrast(enhanced)

    return {
        "original": original,
        "grayscale": grayscale,
        "enhanced_2x": enhanced,
    }


def compare_ocr(image_path):
    """Compare OCR outputs across preprocessing and PSM settings."""
    variants = prepare_images(image_path)
    results = []

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for variant_name, image in variants.items():
        for psm in PSM_MODES:
            text = pytesseract.image_to_string(
                image,
                lang="eng",
                config=f"--psm {psm}",
            ).strip()

            results.append({
                "image": image_path.name,
                "variant": variant_name,
                "psm": psm,
                "extracted_text": text,
                "text_detected": bool(text),
                "character_count": len(text),
            })

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Compare OCR preprocessing configurations."
    )
    parser.add_argument("image_path")
    args = parser.parse_args()

    image_path = Path(args.image_path).expanduser().resolve()

    if not image_path.is_file():
        parser.error(f"Image not found: {image_path}")

    results = compare_ocr(image_path)

    output_path = (
        OUTPUT_DIR / f"{image_path.stem}_comparison.csv"
    )

    with output_path.open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys()),
        )
        writer.writeheader()
        writer.writerows(results)

    print("=== EXP-005B OCR Preprocessing Comparison ===")
    print(f"Image: {image_path.name}")
    print(f"Configurations tested: {len(results)}")

    for result in results:
        print(
            f"\nVariant: {result['variant']} "
            f"| PSM: {result['psm']}"
        )
        print(f"Characters: {result['character_count']}")
        print("Extracted text:")
        print(result["extracted_text"] or "No text detected.")

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()

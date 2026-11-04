
import csv
from pathlib import Path

import pytesseract
from PIL import Image, ImageOps, UnidentifiedImageError


PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMAGE_DIR = PROJECT_ROOT / "data/ocr_samples"
OUTPUT_DIR = PROJECT_ROOT / "reports/ocr"

SUPPORTED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"
}

CONFIGURATIONS = [
    ("original", 6),
    ("grayscale", 11),
]


def extract_ocr(image_path, variant, psm):
    """Extract text using a selected OCR configuration."""
    with Image.open(image_path) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")

    if variant == "grayscale":
        image = ImageOps.grayscale(image)

    text = pytesseract.image_to_string(
        image,
        lang="eng",
        config=f"--psm {psm}",
    ).strip()

    return text


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    image_paths = sorted(
        path for path in IMAGE_DIR.iterdir()
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not image_paths:
        raise FileNotFoundError(
            f"No supported images found in {IMAGE_DIR}"
        )

    results = []

    print("=== EXP-005C Batch OCR Evaluation ===")
    print(f"Images found: {len(image_paths)}")

    for image_path in image_paths:
        print(f"\nImage: {image_path.name}")

        for variant, psm in CONFIGURATIONS:
            try:
                text = extract_ocr(image_path, variant, psm)

                results.append({
                    "image": image_path.name,
                    "variant": variant,
                    "psm": psm,
                    "extracted_text": text,
                    "text_detected": bool(text),
                    "character_count": len(text),
                    "error": "",
                })

                print(f"\nConfiguration: {variant} | PSM {psm}")
                print(text if text else "No text detected.")

            except (
                OSError,
                UnidentifiedImageError,
                pytesseract.TesseractError,
            ) as error:
                results.append({
                    "image": image_path.name,
                    "variant": variant,
                    "psm": psm,
                    "extracted_text": "",
                    "text_detected": False,
                    "character_count": 0,
                    "error": str(error),
                })
                print(f"Error: {error}")

    output_path = OUTPUT_DIR / "batch_ocr_results.csv"

    with output_path.open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys()),
        )
        writer.writeheader()
        writer.writerows(results)

    print("\n=== Summary ===")
    print(f"Images processed: {len(image_paths)}")
    print(f"Configurations per image: {len(CONFIGURATIONS)}")
    print(f"Total evaluations: {len(results)}")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()

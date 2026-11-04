import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pytesseract
from PIL import Image, ImageOps, UnidentifiedImageError


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "reports/ocr"


def extract_text(image_path):
    """Extract raw text from a medication packaging image."""
    image_path = Path(image_path).expanduser().resolve()

    if not image_path.is_file():
        raise FileNotFoundError(
            f"Image file not found: {image_path}"
        )

    with Image.open(image_path) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")

    extracted_text = pytesseract.image_to_string(
        image,
        lang="eng",
        config="--psm 3",
    ).strip()

    return {
        "image_path": str(image_path),
        "ocr_engine": "Tesseract",
        "ocr_version": str(pytesseract.get_tesseract_version()),
        "language": "eng",
        "page_segmentation_mode": 3,
        "extracted_text": extracted_text,
        "text_detected": bool(extracted_text),
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }


def save_result(result):
    """Save the OCR result as a JSON file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    image_path = Path(result["image_path"])
    output_path = OUTPUT_DIR / f"{image_path.stem}_ocr.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from a medication packaging image."
    )
    parser.add_argument(
        "image_path",
        help="Path to the input image.",
    )
    args = parser.parse_args()

    try:
        result = extract_text(args.image_path)
        output_path = save_result(result)

        print("=== EXP-005A OCR Text Extraction ===")
        print(f"Image: {result['image_path']}")
        print(f"OCR engine: {result['ocr_engine']}")
        print(f"OCR version: {result['ocr_version']}")
        print(f"Text detected: {result['text_detected']}")

        print("\n=== Extracted Text ===")
        print(
            result["extracted_text"]
            if result["text_detected"]
            else "No text detected."
        )

        print(f"\nResult saved to: {output_path}")

    except (
        FileNotFoundError,
        UnidentifiedImageError,
        pytesseract.TesseractError,
        pytesseract.TesseractNotFoundError,
        OSError,
    ) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()


"""
EXP-005I: Perspective OCR Integration Test

Tests the integration between perspective-corrected OCR,
medication entity recognition, candidate resolution,
and identity verification.

User confirmation is simulated for development testing only.
"""

import importlib.util
from pathlib import Path

import cv2
import pytesseract


PROJECT_ROOT = Path(__file__).resolve().parents[2]

IMAGE_PATH = (
    PROJECT_ROOT
    / "reports/ocr/medication_02_rectified.jpg"
)

RETRIEVAL_DIR = PROJECT_ROOT / "src/retrieval"


def load_module(filename, module_name):
    """Load an existing retrieval module."""
    path = RETRIEVAL_DIR / filename

    spec = importlib.util.spec_from_file_location(
        module_name,
        path,
    )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def run_integration_test():
    """Run the complete perspective OCR integration test."""

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
        "medication_candidate_resolution",
    )

    verification_module = load_module(
        "09_medication_identity_verification.py",
        "medication_identity_verification",
    )

    medications = matching.load_medications()

    image = cv2.imread(str(IMAGE_PATH))

    if image is None:
        raise FileNotFoundError(IMAGE_PATH)

    # Step 1: OCR
    ocr_text = pytesseract.image_to_string(
        image,
        config="--oem 3 --psm 11",
    )

    # Step 2: Medication Entity Recognition
    recognition_result = recognition.recognize_medication(
        ocr_text,
        medications,
        matching.normalize_name,
    )

    # Step 3: Candidate Resolution
    resolution = resolver.resolve_medication(
        ocr_text,
        medications,
        matching,
        recognition,
    )

    # Step 4: Identity Verification
    verification = verification_module.prepare_verification(
        ocr_text,
        resolver,
        medications,
        matching,
        recognition,
    )

    # Print integration results
    print("EXP-005I: Perspective OCR Integration Test")
    print("=" * 55)

    print("\n[1] OCR RESULT")
    print(ocr_text.strip())

    print("\n[2] ENTITY RECOGNITION")
    print("Status:", recognition_result["status"])

    for entity in recognition_result["entities"]:
        print("Medication:", entity["name"])
        print("Document IDs:", entity["document_ids"])

    print("\n[3] CANDIDATE RESOLUTION")
    print("Status:", resolution["status"])

    print("\n[4] IDENTITY VERIFICATION")
    print("Status:", verification["status"])
    print(
        "Requires User Confirmation:",
        verification["requires_user_confirmation"],
    )

    for candidate in verification["candidates"]:
        print("Candidate:", candidate["name"])
        print("Document IDs:", candidate["document_ids"])

    # Development test: simulate user confirmation.
    if verification["candidates"]:
        selected_ids = [
            verification["candidates"][0]["document_ids"][0]
        ]

        confirmed = verification_module.confirm_medications(
            verification,
            selected_ids,
        )

        print("\n[5] SIMULATED USER CONFIRMATION")

        for selected in confirmed["selected_medications"]:
            print("Selected:", selected["name"])
            print("Document ID:", selected["document_id"])

        print("Final Status:", confirmed["status"])

    else:
        print("\n[5] USER CONFIRMATION")
        print("No candidate available for confirmation.")

    print("\nIntegration test completed.")


if __name__ == "__main__":
    run_integration_test()


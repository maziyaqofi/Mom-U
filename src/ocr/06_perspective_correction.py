
"""
EXP-005I: Perspective Correction for Medication Packaging OCR

This script extracts and rectifies the top surface of a medication
package using OpenCV perspective transformation.
"""

import cv2
import numpy as np
from pathlib import Path


# --------------------------------------------------
# Configuration
# --------------------------------------------------

INPUT_PATH = Path("data/ocr_samples/medication_02.jpg")
OUTPUT_PATH = Path("reports/ocr/medication_02_perspective_corrected.jpg")

# Approximate corner coordinates in the original image.
# Point order: top-left, top-right, bottom-right, bottom-left.
SOURCE_POINTS = np.float32([
    [1723, 209],
    [2217, 438],
    [1395, 999],
    [904, 674]
])


# --------------------------------------------------
# Perspective Correction
# --------------------------------------------------

def calculate_output_dimensions(points):
    top_left, top_right, bottom_right, bottom_left = points

    width_top = np.linalg.norm(top_right - top_left)
    width_bottom = np.linalg.norm(bottom_right - bottom_left)

    height_right = np.linalg.norm(bottom_right - top_right)
    height_left = np.linalg.norm(bottom_left - top_left)

    output_width = int(max(width_top, width_bottom))
    output_height = int(max(height_right, height_left))

    return output_width, output_height


def correct_perspective(image, source_points):
    output_width, output_height = calculate_output_dimensions(
        source_points
    )

    destination_points = np.float32([
        [0, 0],
        [output_width - 1, 0],
        [output_width - 1, output_height - 1],
        [0, output_height - 1]
    ])

    transform_matrix = cv2.getPerspectiveTransform(
        source_points,
        destination_points
    )

    corrected_image = cv2.warpPerspective(
        image,
        transform_matrix,
        (output_width, output_height)
    )

    return corrected_image


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    image = cv2.imread(str(INPUT_PATH))

    if image is None:
        raise FileNotFoundError(
            f"Image not found: {INPUT_PATH}"
        )

    corrected_image = correct_perspective(
        image,
        SOURCE_POINTS
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    success = cv2.imwrite(
        str(OUTPUT_PATH),
        corrected_image
    )

    if not success:
        raise RuntimeError(
            "Failed to save perspective-corrected image."
        )

    height, width = corrected_image.shape[:2]

    print("Perspective Correction Completed")
    print("=" * 45)
    print(f"Input Image: {INPUT_PATH}")
    print(f"Output Image: {OUTPUT_PATH}")
    print(f"Output Width: {width}")
    print(f"Output Height: {height}")
    print(f"Output Aspect Ratio: {width / height:.3f}")


if __name__ == "__main__":
    main()

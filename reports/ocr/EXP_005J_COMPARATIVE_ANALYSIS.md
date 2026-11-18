# MOM-U OCR Comparative Analysis

## 1. Objective

This document summarizes the development and evaluation of OCR-related experiments
conducted for the MOM-U medication information retrieval system.

The objective is to improve medication name recognition from medication packaging
images while preserving a controlled evaluation process.

---

## 2. Experiment Summary

| Experiment | Method | Dataset / Scope | Main Result |
|---|---|---|---|
| Baseline | Original OCR configurations | 9 images | Hit@1: 6/9 (66.67%) |
| EXP-005H | Automatic Multi-Pass OCR | 9 images | Hit@1: 8/9 (88.89%) |
| EXP-005I | Perspective Correction | Single-image case study | Recovered medication_02 |
| EXP-005J | Perspective Correction Evaluation | 2 selected images | medication_08 improved; medication_02 did not |

Baseline and EXP-005H use the same 9-image development evaluation dataset.

EXP-005I and EXP-005J are separate case studies and must not be merged
into the main 9-image evaluation metrics.

---

## 3. Baseline vs. EXP-005H

| Metric | Baseline | EXP-005H |
|---|---:|---:|
| Hit@1 | 6/9 (66.67%) | 8/9 (88.89%) |
| Hit@5 | 6/9 | 8/9 |
| Candidate precision | 6/7 (85.71%) | 8/9 (88.89%) |
| False candidate rate | 1/9 (11.11%) | 1/9 (11.11%) |
| Unresolved cases | 3/9 (33.33%) | 1/9 (11.11%) |
| Explicit recognition | 5/9 (55.56%) | 6/9 (66.67%) |

EXP-005H improved Hit@1 by 22.22 percentage points relative to baseline
and reduced unresolved images from 3 to 1.

These results represent development dataset performance and do not establish
clinical accuracy or generalization to unseen images.

---

## 4. EXP-005I: Perspective Correction Case Study

EXP-005I applied manual perspective correction to medication_02.

The corrected image allowed recovery of the explicit medication entity
"ibuprofen" through the OCR-to-entity recognition pipeline.

This experiment represents a single-image case study and is not included
in the primary 9-image evaluation metrics.

---

## 5. EXP-005J: Perspective Correction Evaluation

### Scope

Two images were evaluated:

- medication_02: ibuprofen, 200 mg
- medication_08: paracetamol, 500 mg

Each image was tested using:

- Original image
- Perspective-corrected image
- PSM 6
- PSM 11
- Grayscale preprocessing

Four OCR configurations were evaluated for each image-condition pair.

### Results

| Image | Condition | Name Recognition | Strength Recognition | Complete Recognition |
|---|---|---:|---:|---:|
| medication_02 | Original | 0/4 | 0/4 | 0/4 |
| medication_02 | Corrected | 0/4 | 0/4 | 0/4 |
| medication_08 | Original | 0/4 | 0/4 | 0/4 |
| medication_08 | Corrected | 4/4 | 4/4 | 4/4 |

### Interpretation

Perspective correction improved OCR recognition for medication_08.
All four tested configurations successfully recognized the target medication name
and strength from the corrected image.

Perspective correction did not improve medication_02 in the tested configurations.

The results indicate image-dependent benefits rather than universal improvement.

### Limitations

- Only two images were evaluated.
- Corner points were manually selected.
- The evaluation was not conducted on an independent held-out dataset.
- Repeated OCR configurations on the same image are not independent samples.
- The experiment does not establish generalized OCR accuracy.

---

## 6. Recommended OCR Pipeline Strategy

The experiments support the following development strategy:

1. Perform initial OCR on the original image.
2. Assess OCR output quality.
3. Use multi-pass OCR as a recovery strategy.
4. Consider perspective correction only for suitable images.
5. Perform medication entity recognition.
6. Resolve medication candidates.
7. Require user confirmation before treating medication identity as verified.
8. Retrieve verified medication information from the document corpus.

Perspective correction should remain optional until automatic plane detection
and corner-point estimation can be implemented and evaluated reliably.

---

## 7. Research Findings

### Finding 1
Automatic multi-pass OCR improved medication recognition on the 9-image
development dataset compared with the baseline.

### Finding 2
Multiple preprocessing and OCR configurations can improve recovery of medication
information when a single configuration fails.

### Finding 3
Perspective correction provided improvement for medication_08 but not
medication_02 under the tested configurations.

### Finding 4
Image preprocessing should be condition-dependent rather than universally applied.

### Finding 5
OCR output must not be treated as verified medication identity.
Medication entity recognition, candidate resolution, and user confirmation
remain necessary.

---

## 8. Conclusion

Automatic multi-pass OCR is currently the primary OCR recovery strategy
supported by the development dataset results.

Perspective correction remains an optional experimental recovery method.
Its potential benefit is demonstrated in a limited case study, but further
evaluation using a larger and more diverse image dataset is required.

The current findings are preliminary and do not represent clinical validation.

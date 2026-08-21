"""
estimator.py — Improved Disease Severity Estimation Service

Estimates the percentage of visible leaf tissue affected by disease.

IMPORTANT:
    This is still a computer-vision heuristic, not a learned disease
    segmentation model. It is designed to produce a more stable severity
    estimate than the previous "non-green = diseased" implementation.

Pipeline:
    1. Get the preprocessed leaf image.
    2. Build a reliable leaf mask.
    3. Identify healthy-green pixels.
    4. Identify likely disease-symptom pixels using multiple colour cues:
         - yellow / chlorotic regions
         - brown / necrotic regions
         - dark necrotic regions
         - low-saturation abnormal regions
    5. Remove small isolated noise.
    6. Apply morphological cleanup.
    7. Calculate:
            affected_area = diseased_pixels / leaf_pixels
            severity_percent = affected_area * 100
    8. Map percentage to Mild / Moderate / Severe.

Contract:
    Input:
        context["image"]["leaf_crop"]  — numpy BGR array
        context["status"]["preprocessing"] — must be "completed"

    Output:
        context["severity"]["percent"]        — float
        context["severity"]["affected_area"]  — float 0-1
        context["severity"]["bucket"]         — "Mild" | "Moderate" | "Severe"
        context["status"]["severity"]         — "completed" | "skipped" | "failed"

Notes:
    - The result is an estimate of visually abnormal leaf area.
    - It should NOT be interpreted as a laboratory-grade measurement.
    - A dedicated segmentation model is the next step if production-level
      severity accuracy is required.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np

# ============================================================================
# CONFIGURATION
# ============================================================================

MIN_LEAF_PIXELS = 500
MIN_COMPONENT_AREA = 30
MORPH_KERNEL_SIZE = 5

HEALTHY_GREEN_LOWER = np.array([30, 35, 35], dtype=np.uint8)
HEALTHY_GREEN_UPPER = np.array([95, 255, 255], dtype=np.uint8)

YELLOW_LOWER = np.array([15, 45, 45], dtype=np.uint8)
YELLOW_UPPER = np.array([35, 255, 255], dtype=np.uint8)

BROWN_LOWER = np.array([5, 35, 20], dtype=np.uint8)
BROWN_UPPER = np.array([25, 255, 190], dtype=np.uint8)

DARK_LOWER = np.array([0, 20, 0], dtype=np.uint8)
DARK_UPPER = np.array([179, 255, 70], dtype=np.uint8)

PALE_LOWER = np.array([0, 0, 100], dtype=np.uint8)
PALE_UPPER = np.array([179, 80, 255], dtype=np.uint8)

# ============================================================================
# PUBLIC API
# ============================================================================

def estimate_severity(context: dict) -> dict:
    """Estimate visually affected leaf area."""
    if context["status"]["preprocessing"] != "completed":
        context["status"]["severity"] = "skipped"
        context["notes"].append(
            "Severity estimation skipped because preprocessing did not complete."
        )
        return context

    image_bgr = context["image"].get("leaf_crop")

    if image_bgr is None:
        processed_path = context["image"].get("processed_path")

        if not processed_path:
            context["notes"].append(
                "No processed image available for severity estimation."
            )
            context["status"]["severity"] = "failed"
            return context

        image_path = Path(processed_path)

        if not image_path.exists():
            context["notes"].append(
                f"Processed image not found: {image_path}"
            )
            context["status"]["severity"] = "failed"
            return context

        image_bgr = cv2.imread(
            str(image_path),
            cv2.IMREAD_COLOR,
        )

        if image_bgr is None:
            context["notes"].append(
                f"Could not read processed image: {image_path}"
            )
            context["status"]["severity"] = "failed"
            return context

    if not isinstance(image_bgr, np.ndarray):
        context["notes"].append(
            "Severity estimation received an invalid image object."
        )
        context["status"]["severity"] = "failed"
        return context

    if image_bgr.size == 0:
        context["notes"].append(
            "Severity estimation received an empty image."
        )
        context["status"]["severity"] = "failed"
        return context

    if len(image_bgr.shape) != 3 or image_bgr.shape[2] != 3:
        context["notes"].append(
            "Severity estimation requires a 3-channel BGR image."
        )
        context["status"]["severity"] = "failed"
        return context

    percent, affected_area = _compute_severity(image_bgr)

    if percent is None or affected_area is None:
        context["notes"].append(
            "Severity estimation failed — could not obtain a reliable leaf mask."
        )
        context["status"]["severity"] = "failed"
        return context

    bucket = _severity_bucket(percent)

    context["severity"]["percent"] = round(float(percent), 2)
    context["severity"]["affected_area"] = round(float(affected_area), 4)
    context["severity"]["bucket"] = bucket
    context["status"]["severity"] = "completed"

    return context

# ============================================================================
# CORE SEVERITY COMPUTATION
# ============================================================================

def _compute_severity(
    image_bgr: np.ndarray,
) -> Tuple[Optional[float], Optional[float]]:
    """Compute visually abnormal leaf area."""
    hsv = cv2.cvtColor(
        image_bgr,
        cv2.COLOR_BGR2HSV,
    )
    lab = cv2.cvtColor(
        image_bgr,
        cv2.COLOR_BGR2LAB,
    )

    leaf_mask = _build_leaf_mask(
        image_bgr=image_bgr,
        hsv=hsv,
    )

    total_leaf_pixels = int(
        np.count_nonzero(leaf_mask)
    )

    if total_leaf_pixels < MIN_LEAF_PIXELS:
        return None, None

    disease_mask = _build_disease_mask(
        image_bgr=image_bgr,
        hsv=hsv,
        lab=lab,
        leaf_mask=leaf_mask,
    )

    disease_mask = _clean_binary_mask(
        disease_mask
    )

    disease_mask = cv2.bitwise_and(
        disease_mask,
        leaf_mask,
    )

    disease_mask = _remove_small_components(
        disease_mask,
        min_area=MIN_COMPONENT_AREA,
    )

    diseased_pixels = int(
        np.count_nonzero(disease_mask)
    )

    affected_area = (
        diseased_pixels / total_leaf_pixels
    )

    severity_percent = affected_area * 100.0

    affected_area = float(
        np.clip(
            affected_area,
            0.0,
            1.0,
        )
    )

    severity_percent = float(
        np.clip(
            severity_percent,
            0.0,
            100.0,
        )
    )

    return severity_percent, affected_area

# ============================================================================
# LEAF MASK
# ============================================================================

def _build_leaf_mask(
    image_bgr: np.ndarray,
    hsv: np.ndarray,
) -> np.ndarray:
    """Build a conservative mask for actual leaf tissue."""
    vegetation_lower = np.array(
        [15, 25, 20],
        dtype=np.uint8,
    )
    vegetation_upper = np.array(
        [100, 255, 255],
        dtype=np.uint8,
    )

    vegetation_mask = cv2.inRange(
        hsv,
        vegetation_lower,
        vegetation_upper,
    )

    green_mask = cv2.inRange(
        hsv,
        HEALTHY_GREEN_LOWER,
        HEALTHY_GREEN_UPPER,
    )

    leaf_mask = cv2.bitwise_or(
        vegetation_mask,
        green_mask,
    )

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (
            MORPH_KERNEL_SIZE,
            MORPH_KERNEL_SIZE,
        ),
    )

    leaf_mask = cv2.morphologyEx(
        leaf_mask,
        cv2.MORPH_OPEN,
        kernel,
        iterations=1,
    )

    leaf_mask = cv2.morphologyEx(
        leaf_mask,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2,
    )

    leaf_mask = _remove_small_components(
        leaf_mask,
        min_area=max(
            MIN_COMPONENT_AREA,
            int(image_bgr.shape[0] * image_bgr.shape[1] * 0.002),
        ),
    )

    leaf_mask = _keep_relevant_leaf_regions(
        leaf_mask
    )

    return leaf_mask

# ============================================================================
# DISEASE MASK
# ============================================================================

def _build_disease_mask(
    image_bgr: np.ndarray,
    hsv: np.ndarray,
    lab: np.ndarray,
    leaf_mask: np.ndarray,
) -> np.ndarray:
    """Detect likely visually abnormal regions inside the leaf."""
    yellow_mask = cv2.inRange(
        hsv,
        YELLOW_LOWER,
        YELLOW_UPPER,
    )

    brown_mask = cv2.inRange(
        hsv,
        BROWN_LOWER,
        BROWN_UPPER,
    )

    dark_mask = cv2.inRange(
        hsv,
        DARK_LOWER,
        DARK_UPPER,
    )

    pale_mask = cv2.inRange(
        hsv,
        PALE_LOWER,
        PALE_UPPER,
    )

    disease_mask = cv2.bitwise_or(
        yellow_mask,
        brown_mask,
    )

    disease_mask = cv2.bitwise_or(
        disease_mask,
        dark_mask,
    )

    disease_mask = cv2.bitwise_or(
        disease_mask,
        pale_mask,
    )

    disease_mask = cv2.bitwise_and(
        disease_mask,
        leaf_mask,
    )

    disease_mask = _filter_weak_candidates(
        disease_mask=disease_mask,
        hsv=hsv,
        lab=lab,
        leaf_mask=leaf_mask,
    )

    return disease_mask

# ============================================================================
# CANDIDATE FILTERING
# ============================================================================

def _filter_weak_candidates(
    disease_mask: np.ndarray,
    hsv: np.ndarray,
    lab: np.ndarray,
    leaf_mask: np.ndarray,
) -> np.ndarray:
    """Remove weak colour anomalies."""
    if np.count_nonzero(disease_mask) == 0:
        return disease_mask

    h = hsv[:, :, 0]
    s = hsv[:, :, 1]
    v = hsv[:, :, 2]

    l_channel = lab[:, :, 0]
    a_channel = lab[:, :, 1]
    b_channel = lab[:, :, 2]

    strong_yellow = (
        (h >= 18)
        & (h <= 38)
        & (s >= 60)
        & (v >= 70)
    )

    strong_brown = (
        (h >= 5)
        & (h <= 28)
        & (s >= 45)
        & (v >= 25)
        & (v <= 190)
    )

    strong_dark = (
        (v <= 65)
        & (s >= 25)
    )

    pale_abnormal = (
        (s <= 75)
        & (v >= 120)
        & (l_channel >= 130)
        & (b_channel >= 125)
    )

    lab_abnormal = (
        (
            (a_channel >= 125)
            & (b_channel >= 135)
        )
        |
        (
            (a_channel >= 135)
            & (b_channel >= 125)
        )
    )

    strong_candidate = (
        strong_yellow
        | strong_brown
        | strong_dark
        | pale_abnormal
        | lab_abnormal
    )

    strong_candidate = (
        strong_candidate.astype(np.uint8)
        * 255
    )

    filtered = cv2.bitwise_and(
        disease_mask,
        strong_candidate,
    )

    filtered = cv2.bitwise_and(
        filtered,
        leaf_mask,
    )

    return filtered

# ============================================================================
# MORPHOLOGICAL CLEANUP
# ============================================================================

def _clean_binary_mask(
    mask: np.ndarray,
) -> np.ndarray:
    """Remove isolated pixels and fill small gaps."""
    if mask is None or mask.size == 0:
        return mask

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (
            MORPH_KERNEL_SIZE,
            MORPH_KERNEL_SIZE,
        ),
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel,
        iterations=1,
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=1,
    )

    return mask

# ============================================================================
# CONNECTED COMPONENT FILTER
# ============================================================================

def _remove_small_components(
    mask: np.ndarray,
    min_area: int,
) -> np.ndarray:
    """Remove connected components smaller than min_area."""
    if mask is None or mask.size == 0:
        return mask

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask,
        connectivity=8,
    )

    cleaned = np.zeros_like(mask)

    for label_id in range(1, num_labels):
        area = int(
            stats[label_id, cv2.CC_STAT_AREA]
        )

        if area >= min_area:
            cleaned[labels == label_id] = 255

    return cleaned

# ============================================================================
# RELEVANT LEAF REGION SELECTION
# ============================================================================

def _keep_relevant_leaf_regions(
    mask: np.ndarray,
) -> np.ndarray:
    """Keep the largest meaningful leaf regions."""
    if mask is None or mask.size == 0:
        return mask

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask,
        connectivity=8,
    )

    components = []

    for label_id in range(1, num_labels):
        area = int(
            stats[label_id, cv2.CC_STAT_AREA]
        )

        if area > 0:
            components.append(
                (label_id, area)
            )

    if not components:
        return np.zeros_like(mask)

    components.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    largest_area = components[0][1]

    keep_labels = []

    for label_id, area in components:
        if area >= largest_area * 0.20:
            keep_labels.append(label_id)

    result = np.zeros_like(mask)

    for label_id in keep_labels:
        result[labels == label_id] = 255

    return result

# ============================================================================
# SEVERITY BUCKET
# ============================================================================

def _severity_bucket(
    percent: float,
) -> str:
    """Map severity percentage to a human-readable bucket."""
    if percent < 20.0:
        return "Mild"

    if percent <= 50.0:
        return "Moderate"

    return "Severe"
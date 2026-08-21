"""
leaf_isolator.py — Subject leaf isolation using colour + sharpness + position scoring.

Ported from notebooks/03_leaf_segmentation.ipynb.

Strategy: colour thresholding alone can't tell "the leaf you're photographing"
apart from "other green leaves in the background".  Two additional cues help:

  1. FOCUS: farmers instinctively focus the camera on the target leaf, so
     background leaves are usually slightly out of focus (lower local sharpness).
  2. POSITION / SIZE: the subject leaf is almost always the largest and most
     central green region in the frame.

All three cues (colour + sharpness + position/size) are combined into a single
composite score per candidate contour.  The winner is cropped out with padding.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional


def compute_sharpness_map(gray: np.ndarray, ksize: int = 25) -> np.ndarray:
    """
    Local sharpness via a sliding-window Laplacian variance map.

    Args:
        gray:  Single-channel (grayscale) image.
        ksize: Kernel size for the local averaging window.

    Returns:
        A float map where higher values = sharper / more in-focus pixels.
    """
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    lap_sq = lap ** 2
    local_mean = cv2.blur(lap_sq, (ksize, ksize))
    return local_mean


def green_mask(hsv: np.ndarray) -> np.ndarray:
    """
    Broad green-vegetation mask in HSV space.

    The range is deliberately wide because leaf colour varies with disease and
    lighting.  We rely on sharpness + position to pick the RIGHT green region
    rather than on colour alone to exclude every other green thing.

    Args:
        hsv: Image in HSV colour space.

    Returns:
        Binary mask (uint8, 0 or 255).
    """
    lower = np.array([25, 30, 30])
    upper = np.array([95, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    return mask


def score_contour(
    contour: np.ndarray,
    image_shape: tuple,
    sharpness_map: np.ndarray,
    mask: np.ndarray,
) -> tuple[float, Optional[tuple]]:
    """
    Score a candidate leaf contour on area, centrality, and local sharpness.

    Args:
        contour:       Single contour from cv2.findContours.
        image_shape:   Shape of the source image (h, w, ...).
        sharpness_map: Output of compute_sharpness_map.
        mask:          Green mask (unused in scoring, kept for API symmetry).

    Returns:
        (score, bounding_rect) — score=-1 means the contour is too small.
    """
    h, w = image_shape[:2]
    area = cv2.contourArea(contour)

    if area < 0.005 * h * w:  # ignore tiny specks
        return -1, None

    x, y, bw, bh = cv2.boundingRect(contour)
    cx, cy = x + bw / 2, y + bh / 2
    img_cx, img_cy = w / 2, h / 2
    dist_from_center = np.hypot(cx - img_cx, cy - img_cy)
    max_dist = np.hypot(img_cx, img_cy)
    centrality_score = 1 - (dist_from_center / max_dist)

    region_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.drawContours(region_mask, [contour], -1, 255, thickness=cv2.FILLED)
    mean_sharpness = cv2.mean(sharpness_map, mask=region_mask)[0]

    area_score = area / (h * w)

    # Weighted combination — tune weights here if the wrong leaf keeps winning.
    combined = (
        0.45 * area_score
        + 0.30 * centrality_score
        + 0.25 * min(mean_sharpness / 500, 1.0)
    )
    return combined, (x, y, bw, bh)


def isolate_subject_leaf(
    image_bgr: np.ndarray,
    padding_ratio: float = 0.08,
) -> Optional[np.ndarray]:
    """
    Return the cropped subject-leaf image (BGR), or None if no confident
    candidate was found.

    When None is returned the caller should either:
      - Use the full image as a fallback, or
      - Ask the farmer to retake the photo.

    Args:
        image_bgr:     Source image in BGR colour space (as read by cv2.imread).
        padding_ratio: Fractional padding added around the chosen bounding box.

    Returns:
        Cropped BGR image of the subject leaf, or None.
    """
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    sharpness_map = compute_sharpness_map(gray)
    mask = green_mask(hsv)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    best_score, best_box = -1.0, None
    for c in contours:
        score, box = score_contour(c, image_bgr.shape, sharpness_map, mask)
        if score > best_score:
            best_score, best_box = score, box

    if best_box is None or best_score < 0.15:  # confidence floor
        return None

    x, y, bw, bh = best_box
    pad_x, pad_y = int(bw * padding_ratio), int(bh * padding_ratio)
    h, w = image_bgr.shape[:2]
    x0, y0 = max(0, x - pad_x), max(0, y - pad_y)
    x1, y1 = min(w, x + bw + pad_x), min(h, y + bh + pad_y)

    return image_bgr[y0:y1, x0:x1]

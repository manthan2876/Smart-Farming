"""
leaf_isolator.py — Subject leaf isolation using colour + sharpness + position scoring.
"""

from __future__ import annotations

import cv2
import numpy as np
from typing import Optional


def compute_sharpness_map(gray: np.ndarray, ksize: int = 25) -> np.ndarray:
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    lap_sq = lap**2
    return cv2.blur(lap_sq, (ksize, ksize))


def green_mask(hsv: np.ndarray) -> np.ndarray:
    lower = np.array([25, 30, 30])
    upper = np.array([95, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)


def score_contour(
    contour: np.ndarray,
    image_shape: tuple,
    sharpness_map: np.ndarray,
    mask: np.ndarray,
) -> tuple[float, Optional[tuple]]:
    h, w = image_shape[:2]
    area = cv2.contourArea(contour)

    if area < 0.005 * h * w:
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

    if best_box is None or best_score < 0.15:
        return None

    x, y, bw, bh = best_box
    pad_x, pad_y = int(bw * padding_ratio), int(bh * padding_ratio)
    h, w = image_bgr.shape[:2]
    x0, y0 = max(0, x - pad_x), max(0, y - pad_y)
    x1, y1 = min(w, x + bw + pad_x), min(h, y + bh + pad_y)

    return image_bgr[y0:y1, x0:x1]

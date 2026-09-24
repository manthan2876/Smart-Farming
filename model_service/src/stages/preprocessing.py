"""
preprocessing.py — OpenCV Preprocessing Stage
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, cast

import cv2
import numpy as np

from src.stages.leaf_isolator import isolate_subject_leaf


class OpenCVPreprocessorService:
    def __init__(self, config: dict[str, Any]) -> None:
        self.thresholds = config.get("thresholds", {})
        self.blur_threshold: float = float(self.thresholds.get("blur_var_threshold", 50.0))
        self.min_brightness: float = float(self.thresholds.get("min_brightness", 40.0))
        self.max_brightness: float = float(self.thresholds.get("max_brightness", 240.0))

    def process(self, context: dict) -> dict:
        input_im = context.get("image_bgr")
        if input_im is None:
            raw_path = context.get("image", {}).get("raw_path")
            if raw_path and os.path.exists(raw_path):
                input_im = cv2.imread(raw_path, cv2.IMREAD_COLOR)

        if input_im is None or input_im.size == 0 or input_im.shape[0] < 10 or input_im.shape[1] < 10:
            context["status"]["preprocessing"] = "failed_corrupt_image"
            context.setdefault("notes", []).append("Image is corrupt or unreadable.")
            return context

        # ── A. Global Blur and Brightness Detection ────────────────────
        gray = cv2.cvtColor(input_im, cv2.COLOR_BGR2GRAY)
        blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        context["image"]["blur_score"] = blur_score

        hsv = cv2.cvtColor(input_im, cv2.COLOR_BGR2HSV)
        brightness_score = float(np.mean(hsv[:, :, 2]))
        context["image"]["brightness_score"] = brightness_score

        if not (self.min_brightness <= brightness_score <= self.max_brightness):
            context["image"]["leaf_detected"] = False
            context["status"]["preprocessing"] = "failed_lighting"
            context.setdefault("notes", []).append(
                f"Poor lighting (brightness={brightness_score:.1f}, expected {self.min_brightness}–{self.max_brightness})"
            )
            return context

        # ── B. Leaf Detection + Isolation ─────────────────────────────
        leaf_crop_bgr = isolate_subject_leaf(input_im)
        if leaf_crop_bgr is None or leaf_crop_bgr.size == 0:
            leaf_crop_bgr = self._watershed_leaf_detection(input_im, hsv)

        if leaf_crop_bgr is None:
            context["image"]["leaf_detected"] = False
            context["status"]["preprocessing"] = "failed_no_leaf"
            context.setdefault("notes", []).append("No plant leaf detected in the image.")
            return context

        # ── C. Subject-Specific Sharpness Evaluation ──────────────────
        leaf_gray = cv2.cvtColor(leaf_crop_bgr, cv2.COLOR_BGR2GRAY)
        leaf_blur_score = float(cv2.Laplacian(leaf_gray, cv2.CV_64F).var())
        effective_blur = max(blur_score, leaf_blur_score)
        context["image"]["blur_score"] = effective_blur
        context["image"]["leaf_blur_score"] = leaf_blur_score

        if effective_blur < self.blur_threshold:
            context["image"]["leaf_detected"] = False
            context["status"]["preprocessing"] = "failed_blur"
            context.setdefault("notes", []).append(
                f"Image is too blurry (sharpness score={effective_blur:.1f}, threshold={self.blur_threshold})"
            )
            return context

        context["image"]["leaf_detected"] = True

        # ── E & F. CLAHE Enhancement ───────────────────────────────────
        enhanced = self._apply_clahe(leaf_crop_bgr)

        # ── G. Resize to 224×224 ──────────────────────────────────────
        final_processed = cv2.resize(enhanced, (224, 224), interpolation=cv2.INTER_AREA)

        quality_score = blur_score * 0.5 + brightness_score * 0.5
        context["image"]["quality_score"] = quality_score
        context["image"]["leaf_crop"] = final_processed
        context["status"]["preprocessing"] = "completed"

        return context

    def _watershed_leaf_detection(self, image: np.ndarray, hsv: np.ndarray) -> np.ndarray | None:
        low_H, high_H = 25, 85
        low_S, high_S = 30, 255
        low_V, high_V = 30, 255
        im_threshold = cv2.inRange(hsv, (low_H, low_S, low_V), (high_H, high_S, high_V))

        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(im_threshold, cv2.MORPH_OPEN, kernel, iterations=2)
        sure_bg = cv2.dilate(opening, kernel, iterations=3)

        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        max_distance = dist_transform.max()

        if max_distance == 0:
            return None

        threshold_value = float(0.15 * float(max_distance))
        _, sure_fg = cv2.threshold(dist_transform, threshold_value, 255.0, cv2.THRESH_BINARY)
        sure_fg = np.asarray(sure_fg, dtype=np.uint8)
        unknown = cv2.subtract(cast(Any, sure_bg), cast(Any, sure_fg))

        _, markers = cv2.connectedComponents(cast(Any, sure_fg))
        markers = markers + 1
        markers[unknown == 255] = 0
        markers = cv2.watershed(image, markers)

        valid_mask = np.zeros_like(im_threshold)
        leaf_found = False

        marker_count = int(markers.max())
        if marker_count >= 2:
            for i in range(2, marker_count + 1):
                component_mask = np.asarray(np.uint8(markers == i) * 255)
                contours, _ = cv2.findContours(
                    cast(Any, component_mask), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    x, y, cw, ch = cv2.boundingRect(cnt)
                    if area < 150 or cw < 30 or ch < 30:
                        continue
                    cv2.drawContours(valid_mask, [cnt], -1, 255, thickness=cv2.FILLED)
                    leaf_found = True

        if not leaf_found:
            return None

        masked_img = image.copy()
        masked_img[valid_mask == 0] = [0, 0, 0]
        return masked_img

    @staticmethod
    def _apply_clahe(image: np.ndarray) -> np.ndarray:
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l_channel)
        limg = cv2.merge((cl, a, b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

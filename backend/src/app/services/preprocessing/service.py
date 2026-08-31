"""
service.py — OpenCV Preprocessing Service

Ported from notebooks/opencv-pipeline.ipynb (v3) and extended with the
leaf-isolation logic from notebooks/03_leaf_segmentation.ipynb.

Responsibilities:
  A. Blur detection          — cv2.Laplacian variance
  B. Brightness check        — mean HSV V-channel
  C. Leaf detection          — HSV thresholding + watershed segmentation
  D. Leaf isolation          — leaf_isolator.isolate_subject_leaf (sharpness scoring)
  E. Background removal      — largest contour mask
  F. CLAHE enhancement       — contrast-limited adaptive histogram equalisation
  G. Resize to 224×224
  H. Save processed image to disk
  I. Update context

If any quality check fails the pipeline is short-circuited (context status set
to a failure code) and no model is ever called — this saves compute and gives
the farmer an actionable error message.
"""

import os
from pathlib import Path
from typing import Any, cast

import cv2
import numpy as np

from app.services.preprocessing.leaf_isolator import isolate_subject_leaf


class OpenCVPreprocessorService:
    """
    Stateless OpenCV preprocessing stage.

    Takes a context dict, reads the raw image from context["image"]["raw_path"],
    runs all quality checks and enhancements, writes the processed image to disk,
    and updates context["image"] and context["status"]["preprocessing"].
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Args:
            config: The parsed config.yaml dict (or just the relevant sub-sections).
        """
        self.thresholds = config.get("thresholds", {})
        self.storage = config.get("storage", {})

        self.blur_threshold: float = float(
            self.thresholds.get("blur_var_threshold", 100.0)
        )
        self.min_brightness: float = float(self.thresholds.get("min_brightness", 40.0))
        self.max_brightness: float = float(self.thresholds.get("max_brightness", 240.0))
        self.processed_dir: str = self.storage.get("processed_dir", "processed/")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(self, context: dict) -> dict:
        """
        Run the full preprocessing pipeline on the image referenced in context.

        Returns the mutated context dict.
        """
        raw_path = context["image"]["raw_path"]
        input_im = cv2.imread(raw_path, cv2.IMREAD_COLOR)

        if input_im is None:
            print(f"[Preprocessing] Failed to read image: {raw_path}")
            context["status"]["preprocessing"] = "failed_read"
            return context

        # ── A. Blur Detection ──────────────────────────────────────────
        gray = cv2.cvtColor(input_im, cv2.COLOR_BGR2GRAY)
        blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        context["image"]["blur_score"] = blur_score

        if blur_score < self.blur_threshold:
            print(
                f"[Preprocessing] Image too blurry "
                f"(score={blur_score:.2f} < threshold={self.blur_threshold})"
            )
            context["image"]["leaf_detected"] = False
            context["status"]["preprocessing"] = "failed_blur"
            return context

        # ── B. Brightness Check ────────────────────────────────────────
        hsv = cv2.cvtColor(input_im, cv2.COLOR_BGR2HSV)
        brightness_score = float(np.mean(hsv[:, :, 2]))
        context["image"]["brightness_score"] = brightness_score

        if not (self.min_brightness <= brightness_score <= self.max_brightness):
            print(
                f"[Preprocessing] Poor lighting "
                f"(brightness={brightness_score:.2f}, "
                f"expected {self.min_brightness}–{self.max_brightness})"
            )
            context["image"]["leaf_detected"] = False
            context["status"]["preprocessing"] = "failed_lighting"
            return context

        # ── C & D. Leaf Detection + Isolation ─────────────────────────
        # First try the smarter sharpness-aware isolator (notebook 03).
        leaf_crop_bgr = isolate_subject_leaf(input_im)

        if leaf_crop_bgr is None or leaf_crop_bgr.size == 0:
            # Fall back to the simpler watershed approach from opencv-pipeline.ipynb
            leaf_crop_bgr = self._watershed_leaf_detection(input_im, hsv)

        if leaf_crop_bgr is None:
            context["image"]["leaf_detected"] = False
            context["status"]["preprocessing"] = "failed_no_leaf"
            return context

        context["image"]["leaf_detected"] = True

        # ── E & F. CLAHE Enhancement ───────────────────────────────────
        enhanced = self._apply_clahe(leaf_crop_bgr)

        # ── G. Resize to 224×224 ──────────────────────────────────────
        final_processed = cv2.resize(enhanced, (224, 224), interpolation=cv2.INTER_AREA)

        # ── H. Save Processed Image ────────────────────────────────────
        os.makedirs(self.processed_dir, exist_ok=True)
        processed_filename = Path(raw_path).name
        processed_save_path = os.path.join(self.processed_dir, processed_filename)
        cv2.imwrite(processed_save_path, final_processed)

        # ── I. Update Context ──────────────────────────────────────────
        quality_score = blur_score * 0.5 + brightness_score * 0.5
        context["image"]["processed_path"] = processed_save_path
        context["image"]["quality_score"] = quality_score
        # Store the processed numpy array in-memory so downstream services
        # don't need to re-read from disk.
        context["image"]["leaf_crop"] = final_processed
        context["status"]["preprocessing"] = "completed"

        return context

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _watershed_leaf_detection(
        self,
        image: np.ndarray,
        hsv: np.ndarray,
    ) -> np.ndarray | None:
        """
        Fallback leaf detection using HSV thresholding + watershed segmentation.

        Ported directly from notebooks/opencv-pipeline.ipynb.
        Returns a cropped leaf image or None.
        """
        low_H, high_H = 25, 85
        low_S, high_S = 30, 255
        low_V, high_V = 30, 255
        im_threshold = cv2.inRange(
            hsv,
            (low_H, low_S, low_V),
            (high_H, high_S, high_V),
        )

        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(im_threshold, cv2.MORPH_OPEN, kernel, iterations=2)
        sure_bg = cv2.dilate(opening, kernel, iterations=3)

        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        max_distance = dist_transform.max()

        if max_distance == 0:
            print("[Preprocessing] No plant-like region found (watershed).")
            return None

        threshold_value = float(0.15 * float(max_distance))
        _, sure_fg = cv2.threshold(
            dist_transform, threshold_value, 255.0, cv2.THRESH_BINARY
        )
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
                    cast(Any, component_mask),
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE,
                )
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    x, y, cw, ch = cv2.boundingRect(cnt)
                    if area < 150 or cw < 30 or ch < 30:
                        continue
                    cv2.drawContours(valid_mask, [cnt], -1, 255, thickness=cv2.FILLED)
                    leaf_found = True

        if not leaf_found:
            print("[Preprocessing] No valid leaf contours detected (watershed).")
            return None

        # Apply mask
        masked_img = image.copy()
        masked_img[valid_mask == 0] = [0, 0, 0]
        return masked_img

    @staticmethod
    def _apply_clahe(image: np.ndarray) -> np.ndarray:
        """
        Apply CLAHE (Contrast Limited Adaptive Histogram Equalisation) to the
        L-channel in LAB colour space.  This enhances local contrast without
        washing out colour information.
        """
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l_channel)
        limg = cv2.merge((cl, a, b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

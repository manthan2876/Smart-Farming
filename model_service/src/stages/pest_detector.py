"""
pest_detector.py — Pest Classification Stage (YOLOv8)
"""

from __future__ import annotations
from typing import Any, cast
import cv2
import numpy as np
from src.loader import load_yolo


def predict_pest(context: dict, config: dict[str, Any]) -> dict:
    if context["status"]["preprocessing"] != "completed":
        context["status"]["pest_detection"] = "skipped"
        return context

    pest_cfg = config.get("models", {}).get("pest_classifier", {})
    if not pest_cfg:
        context["status"]["pest_detection"] = "skipped"
        return context

    model_path = pest_cfg.get("path")
    if not model_path:
        context["status"]["pest_detection"] = "skipped"
        return context

    model = load_yolo(model_path)
    if model is None:
        context.setdefault("notes", []).append(f"Pest classifier model unavailable at: {model_path}")
        context["status"]["pest_detection"] = "skipped"
        return context

    image_bgr = context.get("image", {}).get("leaf_crop")
    if image_bgr is None or image_bgr.size == 0:
        context["status"]["pest_detection"] = "skipped"
        return context

    try:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        results = list(model.predict(source=image_rgb, verbose=False))
        if not results:
            context["status"]["pest_detection"] = "failed"
            return context

        result = cast(Any, results[0])
        if result.probs is None:
            context["status"]["pest_detection"] = "failed"
            return context

        raw_probs = result.probs.data
        if hasattr(raw_probs, "cpu"):
            raw_probs = raw_probs.cpu().numpy()
        probs = np.asarray(raw_probs)
        names = result.names

        predictions = []
        all_probs_dict = {}
        for index, probability in enumerate(probs):
            label = str(names.get(index, index))
            conf = float(probability)
            predictions.append({"label": label, "confidence": conf})
            all_probs_dict[label] = conf

        predictions.sort(key=lambda item: item["confidence"], reverse=True)
        detected_pests = [p for p in predictions if p["confidence"] >= 0.40]

        context["pests"] = detected_pests if detected_pests else predictions
        pest_status = "pest_detected" if detected_pests else "no_pest_detected"

        context["pest_classification"] = {
            "model_type": "classification",
            "model_name": "YOLOv8 Pest Classifier",
            "model_used": "pest_classifier.pt",
            "status": pest_status,
            "top_k": 3,
            "top_predictions": predictions[:3],
            "all_probs": all_probs_dict,
            "available": True,
        }
        context["status"]["pest_detection"] = "completed"
    except Exception as exc:
        context.setdefault("notes", []).append(f"Pest detection error: {exc}")
        context["status"]["pest_detection"] = "failed"

    return context

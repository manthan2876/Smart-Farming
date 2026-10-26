"""
pest_detector.py — Pest Classification Stage (YOLOv8)
"""

from __future__ import annotations
import logging
from typing import Any, cast
import cv2
import numpy as np
from ..loader import load_yolo, DEVICE


logger = logging.getLogger(__name__)


def predict_pest(context: dict, config: dict[str, Any]) -> dict:
    if context["status"]["preprocessing"] != "completed":
        context["pest_classification"] = {
            "model_type": "classification",
            "status": "skipped",
            "available": False,
        }
        context["status"]["pest_detection"] = "skipped"
        context["pests"] = []
        return context

    pest_cfg = config.get("models", {}).get("pest_classifier", {})
    if not pest_cfg:
        context["pest_classification"] = {
            "model_type": "classification",
            "model_name": None,
            "model_used": None,
            "status": "unavailable",
            "available": False,
            "message": "Pest classifier not configured.",
        }
        context["status"]["pest_detection"] = "unavailable"
        context["pests"] = []
        return context

    model_path = pest_cfg.get("path")
    if not model_path:
        context["pest_classification"] = {
            "model_type": "classification",
            "model_name": None,
            "model_used": None,
            "status": "unavailable",
            "available": False,
            "message": "Pest classifier path not configured.",
        }
        context["status"]["pest_detection"] = "unavailable"
        context["pests"] = []
        return context

    model = load_yolo(model_path)
    if model is None:
        context.setdefault("notes", []).append(f"Pest classifier model unavailable at: {model_path}")
        context["pest_classification"] = {
            "model_type": "classification",
            "model_name": "YOLOv8 Pest Classifier",
            "model_used": model_path,
            "status": "unavailable",
            "available": False,
            "message": "Pest classifier model weights unavailable on host.",
        }
        context["status"]["pest_detection"] = "unavailable"
        context["pests"] = []
        return context

    image_bgr = context.get("image", {}).get("leaf_crop")
    if image_bgr is None or image_bgr.size == 0:
        context["pest_classification"] = {
            "model_type": "classification",
            "status": "skipped",
            "available": False,
        }
        context["status"]["pest_detection"] = "skipped"
        context["pests"] = []
        return context

    try:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        device = config.get("device", DEVICE)
        results = list(model.predict(source=image_rgb, verbose=False, device=device))
        if not results:
            context["pest_classification"] = {
                "model_type": "classification",
                "status": "failed",
                "available": True,
            }
            context["status"]["pest_detection"] = "failed"
            context["pests"] = []
            return context

        result = cast(Any, results[0])
        if result.probs is None:
            context["pest_classification"] = {
                "model_type": "classification",
                "status": "failed",
                "available": True,
            }
            context["status"]["pest_detection"] = "failed"
            context["pests"] = []
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

        def _is_background_clean_leaf(name: str) -> bool:
            lower = name.lower()
            return any(k in lower for k in ("no pest", "no_pest", "clean", "healthy", "none", "background"))

        # Threshold increased from 0.40 to 0.65 to eliminate false alarms on healthy foliage
        pest_threshold = float(config.get("thresholds", {}).get("pest_confidence", 0.65))
        detected_pests = [
            p for p in predictions
            if p["confidence"] >= pest_threshold and not _is_background_clean_leaf(p["label"])
        ]

        top_pred = predictions[0] if predictions else None
        if top_pred and _is_background_clean_leaf(top_pred["label"]):
            pest_status = "no_pests_detected"
            context["pests"] = []
        elif detected_pests:
            context["pests"] = detected_pests
            pest_status = "pest_detected"
        else:
            context["pests"] = []
            pest_status = "no_pests_detected"

        context["pest_classification"] = {
            "model_type": "pest_damage_classifier",
            "model_name": "YOLOv8 Pest Damage Classifier",
            "model_used": "pest_classifier.pt",
            "status": pest_status,
            "threshold": pest_threshold,
            "top_k": 3,
            "top_predictions": predictions[:3],
            "all_probs": all_probs_dict,
            "available": True,
        }
        context["status"]["pest_detection"] = "completed"
    except Exception as exc:
        logger.error("Pest detection error: %s", exc, exc_info=True)
        context.setdefault("notes", []).append("Pest detection stage encountered an internal error.")
        context["pest_classification"] = {
            "model_type": "classification",
            "status": "failed",
            "available": False,
            "message": "Pest detection failed due to an internal error.",
        }
        context["status"]["pest_detection"] = "failed"
        context["pests"] = []

    return context

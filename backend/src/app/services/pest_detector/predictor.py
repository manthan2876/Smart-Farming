from __future__ import annotations
from pathlib import Path
from typing import Any, cast
import cv2
import numpy as np


def predict_pest(context: dict, config: dict[str, Any]) -> dict:
    if context["status"]["preprocessing"] != "completed":
        context["status"]["pest_detection"] = "skipped"
        context["notes"].append(
            "Pest classification skipped because preprocessing did not complete."
        )
        return context

    pest_cfg = config.get("models", {}).get("pest_classifier", {})
    if not pest_cfg:
        context["notes"].append("Pest classifier is not configured in config.yaml.")
        context["status"]["pest_detection"] = "skipped"
        return context

    model_relative_path = pest_cfg.get("path")
    if not model_relative_path:
        context["notes"].append("Pest classifier model path is missing in config.yaml.")
        context["status"]["pest_detection"] = "skipped"
        return context

    project_root = Path(__file__).resolve().parents[5]
    model_path = (project_root / model_relative_path).resolve()

    if not model_path.exists():
        context["notes"].append(f"Pest classifier model not found at: {model_path}")
        context["status"]["pest_detection"] = "skipped"
        return context

    if not model_path.is_file():
        context["notes"].append(f"Pest classifier path is not a file: {model_path}")
        context["status"]["pest_detection"] = "skipped"
        return context

    try:
        from app.utils.model_loader import load_yolo

        model = load_yolo(model_path)
    except Exception as exc:
        context["notes"].append(
            f"Failed to load pest classifier: {type(exc).__name__}: {exc}"
        )
        context["status"]["pest_detection"] = "failed"
        return context

    if model is None:
        context["notes"].append(f"Could not load pest classifier model: {model_path}")
        context["status"]["pest_detection"] = "skipped"
        return context

    image_bgr = context["image"].get("leaf_crop")
    if image_bgr is None:
        processed_path = context["image"].get("processed_path")
        if not processed_path:
            context["notes"].append(
                "No leaf crop or processed image available for pest classification."
            )
            context["status"]["pest_detection"] = "failed"
            return context

        processed_path = Path(processed_path)
        if not processed_path.is_absolute():
            processed_path = project_root / processed_path
        processed_path = processed_path.resolve()

        if not processed_path.exists():
            context["notes"].append(f"Processed image not found: {processed_path}")
            context["status"]["pest_detection"] = "failed"
            return context

        image_bgr = cv2.imread(str(processed_path), cv2.IMREAD_COLOR)
        if image_bgr is None:
            context["notes"].append(f"Could not read processed image: {processed_path}")
            context["status"]["pest_detection"] = "failed"
            return context

    if not isinstance(image_bgr, np.ndarray):
        context["notes"].append("Pest classification received an invalid image object.")
        context["status"]["pest_detection"] = "failed"
        return context

    if image_bgr.size == 0:
        context["notes"].append("Pest classification received an empty image.")
        context["status"]["pest_detection"] = "failed"
        return context

    try:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        results = list(model.predict(source=image_rgb, verbose=False))

        if not results:
            context["notes"].append("YOLO returned no classification results.")
            context["status"]["pest_detection"] = "failed"
            return context

        result = cast(Any, results[0])
        if result.probs is None:
            context["notes"].append(
                "YOLO result does not contain classification probabilities. "
                "The configured model may not be a classification model."
            )
            context["status"]["pest_detection"] = "failed"
            return context

        raw_probs = result.probs.data
        if hasattr(raw_probs, "cpu"):
            raw_probs = raw_probs.cpu().numpy()
        probs = np.asarray(raw_probs)
        names = result.names

        if probs.size == 0:
            context["notes"].append(
                "YOLO returned an empty classification probability vector."
            )
            context["status"]["pest_detection"] = "failed"
            return context

        predictions = []
        all_probs_dict = {}
        for index, probability in enumerate(probs):
            label = str(names.get(index, index))
            conf = float(probability)
            predictions.append(
                {
                    "label": label,
                    "confidence": conf,
                }
            )
            all_probs_dict[label] = conf

        predictions.sort(key=lambda item: item["confidence"], reverse=True)

        # Populate context["pests"] list expected by test_pipeline.py
        context["pests"] = predictions

        # Populate context["pest_classification"] details
        context["pest_classification"] = {
            "model_type": "classification",
            "model_used": model_path.name,
            "top_k": len(predictions),
            "all_probs": all_probs_dict,
        }

        # Set status back to completed for backward compatibility
        context["status"]["pest_detection"] = "completed"

        primary_prediction = predictions[0]
        pest_confidence = primary_prediction["confidence"]
        pest_confidence_threshold = config.get("thresholds", {}).get(
            "pest_confidence", 0.60
        )

        if pest_confidence < pest_confidence_threshold:
            context["notes"].append(
                f"Pest classification confidence ({pest_confidence:.2f}) is below threshold "
                f"({pest_confidence_threshold:.2f}). Treat this prediction as tentative."
            )

        context["notes"].append(
            "Pest result is a classification prediction. "
            "The current model does not provide pest locations or individual pest counts."
        )

        return context

    except Exception as exc:
        context["notes"].append(
            f"Pest classification error: {type(exc).__name__}: {exc}"
        )
        context["status"]["pest_detection"] = "failed"
        return context

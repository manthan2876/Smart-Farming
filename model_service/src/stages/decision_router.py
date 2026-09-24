"""
decision_router.py — Routes identified crop to the corresponding disease model.
"""

from __future__ import annotations
from typing import Any


def route_to_disease_model(context: dict, config: dict[str, Any]) -> dict:
    if context["status"]["crop_identification"] != "completed":
        context["status"]["decision_routing"] = "skipped"
        return context

    crop_label = context["crop"].get("label")
    crop_confidence = context["crop"].get("confidence", 0.0)
    threshold = config["thresholds"].get("crop_confidence", 0.7)

    if crop_confidence < threshold or context["crop"].get("status") == "unsupported_crop":
        context.setdefault("notes", []).append(
            f"Crop confidence ({crop_confidence:.2f}) is below threshold ({threshold}). Skipping disease classification."
        )
        context["status"]["decision_routing"] = "skipped_low_confidence"
        context["disease"]["label"] = "Indeterminate (Low Crop Confidence)"
        context["disease"]["confidence"] = 0.0
        context["disease"]["model_used"] = "none"
        return context

    # Match crop name to disease models key
    disease_models = config.get("models", {}).get("disease_models", {})
    crop_key = crop_label.replace(" ", "_") if crop_label else ""

    if crop_key not in disease_models and crop_label in disease_models:
        crop_key = crop_label

    if crop_key not in disease_models:
        context.setdefault("notes", []).append(f"No disease classification model available for crop: {crop_label}")
        context["status"]["decision_routing"] = "no_model_available"
        context["disease"]["label"] = "No Model Available"
        context["disease"]["confidence"] = 0.0
        context["disease"]["model_used"] = "none"
        return context

    context["_disease_model_cfg"] = disease_models[crop_key]
    context["disease"]["model_used"] = disease_models[crop_key]["path"]
    context["status"]["decision_routing"] = "completed"
    return context

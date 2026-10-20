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
    crop_status = context["crop"].get("status")

    disease_models = config.get("models", {}).get("disease_models", {})
    supported_crops_str = ", ".join(k.replace("_", " ").title() for k in disease_models.keys()) if disease_models else "Cotton, Groundnut, Pepper Bell, Potato, Tomato"

    # 1. Out-Of-Distribution (OOD) Guard
    if crop_status == "out_of_distribution":
        context["status"]["decision_routing"] = "out_of_distribution"
        context["crop"]["status"] = "unsupported_crop"
        context["crop"]["is_uncertain"] = True
        context["disease"]["label"] = "Indeterminate (Unrecognized Leaf / OOD)"
        context["disease"]["confidence"] = 0.0
        context["disease"]["is_uncertain"] = True
        context["disease"]["model_used"] = "none"
        context["disease"]["requires_expert_review"] = True
        context["disease"]["escalation_reason"] = "out_of_distribution"
        return context

    # 2. Uncertain-Crop Dual-Run Safety Guard (0.50 <= confidence < 0.75)
    if context["crop"].get("is_uncertain_band"):
        top2 = context["crop"].get("top2", [])
        if len(top2) >= 2:
            c1_name = top2[0]["label"]
            c2_name = top2[1]["label"]
            c1_key = c1_name.replace(" ", "_")
            c2_key = c2_name.replace(" ", "_")
            cfg1 = disease_models.get(c1_key) or disease_models.get(c1_name)
            cfg2 = disease_models.get(c2_key) or disease_models.get(c2_name)
            if cfg1 and cfg2:
                context["_dual_run_crops"] = [c1_name, c2_name]
                context["_dual_run_cfgs"] = [cfg1, cfg2]
                context["status"]["decision_routing"] = "completed_uncertain_dual_run"
                context["disease"]["model_used"] = f"dual:{cfg1['path']}|{cfg2['path']}"
                return context

    threshold = config["thresholds"].get("crop_confidence", 0.70)
    if crop_confidence < threshold or crop_status == "unsupported_crop":
        context["crop"]["status"] = "unsupported_crop"
        context["crop"]["is_uncertain"] = True
        context.setdefault("notes", []).append(
            f"Crop confidence ({crop_confidence:.2f}) is below threshold ({threshold}). Automated disease diagnosis requires verified crop identification."
        )
        context["status"]["decision_routing"] = "unsupported_crop"
        context["disease"]["label"] = "Unsupported Crop / Indeterminate"
        context["disease"]["confidence"] = 0.0
        context["disease"]["is_uncertain"] = True
        context["disease"]["model_used"] = "none"
        context["disease"]["requires_expert_review"] = True
        context["disease"]["escalation_reason"] = "crop_confidence_low"
        return context

    # Match crop name to disease models key
    crop_key = crop_label.replace(" ", "_") if crop_label else ""

    if crop_key not in disease_models and crop_label in disease_models:
        crop_key = crop_label

    if crop_key not in disease_models:
        context["crop"]["status"] = "unsupported_crop"
        context["crop"]["is_uncertain"] = True
        context.setdefault("notes", []).append(
            f"Crop '{crop_label}' is currently not supported for automated disease diagnosis. Supported crops: {supported_crops_str}."
        )
        context["status"]["decision_routing"] = "unsupported_crop"
        context["disease"]["label"] = "Unsupported Crop"
        context["disease"]["confidence"] = 0.0
        context["disease"]["is_uncertain"] = True
        context["disease"]["model_used"] = "none"
        return context

    context["_disease_model_cfg"] = disease_models[crop_key]
    context["disease"]["model_used"] = disease_models[crop_key]["path"]
    context["status"]["decision_routing"] = "completed"
    return context


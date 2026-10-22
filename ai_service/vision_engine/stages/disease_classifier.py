"""
disease_classifier.py — Disease Classification Stage (EfficientNet-B2 per crop)
"""

from __future__ import annotations

from typing import Any

import cv2
import torch
import albumentations as A
from albumentations.pytorch import ToTensorV2

from ..loader import load_efficientnet, DEVICE
from .confidence import evaluate_disease_prediction

_EVAL_TF = A.Compose(
    [
        A.Resize(224, 224),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ]
)


def predict_disease(context: dict, config: dict[str, Any]) -> dict:
    routing_status = context["status"].get("decision_routing")
    if routing_status not in ("completed", "completed_uncertain_dual_run"):
        context["status"]["disease_classification"] = "skipped"
        return context

    image_bgr = context.get("image", {}).get("leaf_crop")
    if image_bgr is None:
        context.setdefault("notes", []).append("No processed leaf image available for disease classification.")
        context["status"]["disease_classification"] = "failed"
        return context

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    tensor = _EVAL_TF(image=image_rgb)["image"].unsqueeze(0).to(DEVICE)
    threshold = config.get("thresholds", {}).get("disease_confidence", 0.7)
    near_tie_margin = float(config.get("thresholds", {}).get("near_tie_margin", 0.15))

    # ── A. Handle Uncertain-Crop Top-2 Dual Run ────────────────────────────────
    if routing_status == "completed_uncertain_dual_run":
        crops = context.pop("_dual_run_crops", [])
        cfgs = context.pop("_dual_run_cfgs", [])
        eval_runs = []
        for c_name, c_cfg in zip(crops, cfgs):
            m_res = load_efficientnet(c_cfg["path"], c_cfg["labels"], c_cfg.get("arch", "efficientnet_b2"))
            if m_res:
                m_model, m_classes = m_res
                temp = float(c_cfg.get("temperature", 1.0))
                with torch.no_grad():
                    m_logits = m_model(tensor)
                    m_probs = torch.softmax(m_logits / temp if temp > 0 else m_logits, dim=1).squeeze(0).cpu().numpy()
                eval_runs.append((c_name, evaluate_disease_prediction(m_classes, m_probs, threshold, near_tie_margin)))

        if len(eval_runs) == 2:
            (c1, ev1), (c2, ev2) = eval_runs
            is_h1 = "healthy" in ev1["label"].lower()
            is_h2 = "healthy" in ev2["label"].lower()

            if is_h1 and is_h2:
                context["disease"]["label"] = "Healthy"
                context["disease"]["confidence"] = min(ev1["confidence"], ev2["confidence"])
                context["disease"]["is_uncertain"] = False
                context["disease"]["confidence_rating"] = "high"
                context["disease"]["model_name"] = f"Dual:{c1}|{c2}"
                context["disease"]["all_probs"] = ev1["all_probs"]
                context.setdefault("notes", []).append(
                    f"Dual-crop consensus: leaf classified as Healthy under both {c1} ({ev1['confidence']:.2f}) and {c2} ({ev2['confidence']:.2f}) diagnostic models."
                )
            else:
                context["disease"]["label"] = f"{ev1['label']} ({c1}) / {ev2['label']} ({c2})"
                context["disease"]["confidence"] = max(ev1["confidence"], ev2["confidence"])
                context["disease"]["is_uncertain"] = True
                context["disease"]["confidence_rating"] = "conflict"
                context["disease"]["requires_expert_review"] = True
                context["disease"]["escalation_reason"] = "uncertain_crop_conflict"
                context["disease"]["all_probs"] = ev1["all_probs"]
                context.setdefault("notes", []).append(
                    f"Uncertain crop prediction ({c1} vs {c2}) caused conflicting disease diagnoses ('{ev1['label']}' vs '{ev2['label']}'). Escalated to agronomist review."
                )
            context["status"]["disease_classification"] = "completed"
            return context

    # ── B. Standard Single Crop Disease Run ────────────────────────────────────
    model_cfg = context.pop("_disease_model_cfg", None)
    if not model_cfg:
        context["status"]["disease_classification"] = "skipped"
        return context

    model_path = model_cfg["path"]
    labels_path = model_cfg["labels"]
    arch = model_cfg.get("arch", "efficientnet_b2")

    result = load_efficientnet(model_path, labels_path, arch)
    if result is None:
        context.setdefault("notes", []).append(f"Disease model not found at {model_path}.")
        context["status"]["disease_classification"] = "failed"
        return context

    model, classes = result

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    tensor = _EVAL_TF(image=image_rgb)["image"].unsqueeze(0).to(DEVICE)
    temperature = float(model_cfg.get("temperature", 1.0))
    is_calibrated = bool(temperature > 0 and temperature != 1.0)
    with torch.no_grad():
        logits = model(tensor)
        if is_calibrated:
            probs = torch.softmax(logits / temperature, dim=1).squeeze(0).cpu().numpy()
        else:
            probs = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()

    threshold = config.get("thresholds", {}).get("disease_confidence", 0.7)
    near_tie_margin = float(config.get("thresholds", {}).get("near_tie_margin", 0.15))

    eval_res = evaluate_disease_prediction(classes, probs, threshold, near_tie_margin)

    context["disease"]["label"] = eval_res["label"]
    context["disease"]["confidence"] = eval_res["confidence"]
    context["disease"]["all_probs"] = eval_res["all_probs"]
    context["disease"]["model_name"] = "EfficientNet-B2"
    context["disease"]["model_version"] = "v1.0"
    context["disease"]["is_calibrated"] = is_calibrated
    context["disease"]["temperature"] = temperature
    context["disease"]["is_near_tie"] = eval_res["is_near_tie"]
    context["disease"]["confidence_rating"] = eval_res["confidence_rating"]
    context["disease"]["is_uncertain"] = eval_res["is_uncertain"]
    context["disease"]["uncertainty"] = eval_res["uncertainty"]
    if eval_res["could_also_be"]:
        context["disease"]["could_also_be"] = eval_res["could_also_be"]
    if eval_res["notes"]:
        context.setdefault("notes", []).extend(eval_res["notes"])

    context["status"]["disease_classification"] = "completed"
    return context

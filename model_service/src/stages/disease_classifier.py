"""
disease_classifier.py — Disease Classification Stage (EfficientNet-B2 per crop)
"""

from __future__ import annotations

from typing import Any
import cv2
import numpy as np
import torch
import albumentations as A
from albumentations.pytorch import ToTensorV2

from src.loader import load_efficientnet, DEVICE

_EVAL_TF = A.Compose(
    [
        A.Resize(224, 224),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ]
)


def evaluate_disease_prediction(
    classes: list[str],
    probs: np.ndarray,
    threshold: float = 0.7,
    near_tie_margin: float = 0.15,
) -> dict[str, Any]:
    sorted_indices = np.argsort(probs)[::-1]
    top_idx = int(sorted_indices[0])
    label = classes[top_idx]
    confidence = float(probs[top_idx])

    second_label: str | None = None
    second_confidence: float = 0.0
    if len(sorted_indices) > 1:
        second_idx = int(sorted_indices[1])
        second_label = classes[second_idx]
        second_confidence = float(probs[second_idx])

    margin = float(confidence - second_confidence) if second_label else 1.0
    all_probs = {cls_name: float(p) for cls_name, p in zip(classes, probs)}

    is_near_tie = bool(
        second_label is not None
        and margin <= near_tie_margin
        and confidence < 0.85
    )

    could_also_be = None
    if second_label and second_confidence >= 0.10:
        could_also_be = {
            "label": second_label,
            "confidence": round(second_confidence, 4),
            "margin": round(margin, 4),
        }

    notes = []
    if is_near_tie:
        confidence_rating = "near_tie"
        is_uncertain = True
        notes.append(
            f"Near-tie diagnosis: primary candidate '{label}' ({confidence*100:.1f}%) is close to '{second_label}' ({second_confidence*100:.1f}%, margin {margin*100:.1f}%). Could also be {second_label}."
        )
    elif confidence >= 0.85:
        confidence_rating = "high"
        is_uncertain = False
    elif confidence >= threshold:
        confidence_rating = "moderate"
        is_uncertain = False
    else:
        confidence_rating = "low"
        is_uncertain = True
        notes.append(
            f"Disease confidence ({confidence:.2f}) is below threshold ({threshold}). Indeterminate diagnosis."
        )

    return {
        "label": label,
        "confidence": confidence,
        "all_probs": all_probs,
        "is_near_tie": is_near_tie,
        "could_also_be": could_also_be,
        "confidence_rating": confidence_rating,
        "is_uncertain": is_uncertain,
        "uncertainty": round(float(1.0 - confidence), 3),
        "notes": notes,
    }


def predict_disease(context: dict, config: dict[str, Any]) -> dict:
    if context["status"]["decision_routing"] != "completed":
        context["status"]["disease_classification"] = "skipped"
        return context

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

    image_bgr = context.get("image", {}).get("leaf_crop")
    if image_bgr is None:
        context.setdefault("notes", []).append("No processed leaf image available for disease classification.")
        context["status"]["disease_classification"] = "failed"
        return context

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

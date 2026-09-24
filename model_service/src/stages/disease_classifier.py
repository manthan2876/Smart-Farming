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
    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()

    top_idx = int(np.argmax(probs))
    label = classes[top_idx]
    confidence = float(probs[top_idx])

    all_probs = {cls_name: float(p) for cls_name, p in zip(classes, probs)}

    context["disease"]["label"] = label
    context["disease"]["confidence"] = confidence
    context["disease"]["all_probs"] = all_probs
    context["disease"]["model_name"] = "EfficientNet-B2"
    context["disease"]["model_version"] = "v1.0"
    context["status"]["disease_classification"] = "completed"

    threshold = config["thresholds"].get("disease_confidence", 0.7)
    context["disease"]["uncertainty"] = round(float(1.0 - confidence), 3)

    if confidence >= 0.85:
        context["disease"]["confidence_rating"] = "high"
    elif confidence >= threshold:
        context["disease"]["confidence_rating"] = "moderate"
    else:
        context["disease"]["confidence_rating"] = "low"
        context["disease"]["is_uncertain"] = True
        context.setdefault("notes", []).append(
            f"Disease confidence ({confidence:.2f}) is below threshold ({threshold}). Indeterminate diagnosis."
        )

    return context

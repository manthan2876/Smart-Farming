"""
crop_identifier.py — Crop Identification Stage (EfficientNet-B0)
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


def predict_crop(context: dict, config: dict[str, Any]) -> dict:
    if context["status"]["preprocessing"] != "completed":
        context["status"]["crop_identification"] = "skipped"
        return context

    crop_cfg = config["models"]["crop_identifier"]
    model_path = crop_cfg["path"]
    labels_path = crop_cfg["labels"]
    arch = crop_cfg.get("arch", "efficientnet_b0")

    result = load_efficientnet(model_path, labels_path, arch)
    if result is None:
        context.setdefault("notes", []).append(f"Crop identifier model not found at {model_path}.")
        context["status"]["crop_identification"] = "failed"
        return context

    model, classes = result

    image_bgr = context.get("image", {}).get("leaf_crop")
    if image_bgr is None:
        context.setdefault("notes", []).append("No processed leaf image available for crop identification.")
        context["status"]["crop_identification"] = "failed"
        return context

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    tensor = _EVAL_TF(image=image_rgb)["image"].unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()

    top_idx = int(np.argmax(probs))
    label = classes[top_idx]
    confidence = float(probs[top_idx])

    context["crop"]["label"] = label
    context["crop"]["confidence"] = confidence
    context["crop"]["model_name"] = "EfficientNet-B0"
    context["crop"]["model_file"] = "crop_identifier_v1.pth"
    context["crop"]["model_version"] = "v1.0"
    context["status"]["crop_identification"] = "completed"

    threshold = config["thresholds"].get("crop_confidence", 0.7)
    context["crop"]["uncertainty"] = round(float(1.0 - confidence), 3)

    if confidence >= 0.85:
        context["crop"]["confidence_rating"] = "high"
    elif confidence >= threshold:
        context["crop"]["confidence_rating"] = "moderate"
    else:
        context["crop"]["confidence_rating"] = "low"

    if confidence < threshold:
        context["crop"]["status"] = "unsupported_crop"
        context["crop"]["is_uncertain"] = True
        context.setdefault("notes", []).append(
            f"Crop confidence ({confidence:.2f}) is below threshold ({threshold}). Flagged for review."
        )
    else:
        context["crop"]["status"] = "supported_crop"
        context["crop"]["is_uncertain"] = False

    return context

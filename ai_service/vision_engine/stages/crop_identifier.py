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

from ..loader import load_efficientnet, DEVICE

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
    temperature = float(crop_cfg.get("temperature", 1.0))
    is_calibrated = bool(temperature > 0 and temperature != 1.0)
    with torch.no_grad():
        logits = model(tensor)
        if is_calibrated:
            probs = torch.softmax(logits / temperature, dim=1).squeeze(0).cpu().numpy()
        else:
            probs = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()

    top_indices = np.argsort(probs)[::-1]
    top_idx = int(top_indices[0])
    label = classes[top_idx]
    confidence = float(probs[top_idx])

    top2 = [
        {"label": str(classes[idx]), "confidence": round(float(probs[idx]), 4)}
        for idx in top_indices[:2]
    ]

    # Calculate Shannon entropy for Out-Of-Distribution (OOD) guarding
    entropy = float(-np.sum(probs * np.log(np.clip(probs, 1e-12, 1.0))))

    context["crop"]["label"] = label
    context["crop"]["confidence"] = confidence
    context["crop"]["top2"] = top2
    context["crop"]["entropy"] = round(entropy, 3)
    context["crop"]["model_name"] = "EfficientNet-B0"
    context["crop"]["model_file"] = "crop_identifier_v1.pth"
    context["crop"]["model_version"] = "v1.0"
    context["crop"]["is_calibrated"] = is_calibrated
    context["crop"]["temperature"] = temperature
    context["status"]["crop_identification"] = "completed"

    context["crop"]["uncertainty"] = round(float(1.0 - confidence), 3)

    # 1. Out-Of-Distribution (OOD) Guard (max prob < 0.45 or entropy > 1.5)
    if confidence < 0.45 or entropy > 1.5:
        context["crop"]["status"] = "out_of_distribution"
        context["crop"]["is_uncertain"] = True
        context["crop"]["confidence_rating"] = "low"
        context.setdefault("notes", []).append(
            f"Image is out-of-distribution (confidence={confidence:.2f}, entropy={entropy:.2f}). Not a recognized crop leaf."
        )
        return context

    # 2. Uncertain-Crop Band (0.50 <= confidence < 0.75)
    if confidence < 0.75:
        context["crop"]["confidence_rating"] = "low"
        context["crop"]["status"] = "uncertain_crop"
        context["crop"]["is_uncertain"] = True
        context["crop"]["is_uncertain_band"] = True
        context.setdefault("notes", []).append(
            f"Crop identification is borderline (confidence={confidence:.2f}, top-2: {top2[0]['label']} vs {top2[1]['label']}). Dual-crop safety routing active."
        )
        return context

    # 3. High/Moderate Confidence
    if confidence >= 0.85:
        context["crop"]["confidence_rating"] = "high"
    else:
        context["crop"]["confidence_rating"] = "moderate"

    context["crop"]["status"] = "supported_crop"
    context["crop"]["is_uncertain"] = False
    context["crop"]["is_uncertain_band"] = False

    return context

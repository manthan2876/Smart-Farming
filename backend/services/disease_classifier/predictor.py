"""
predictor.py — Disease Classification Service (per-crop EfficientNet-B2)

Reads the disease model config placed by the Decision Engine, loads the
appropriate per-crop EfficientNet-B2 model, and classifies the disease.

Trained models:
    disease_Cotton.pth        — 8 diseases (val_acc ~94.6%)
    disease_Groundnut.pth     — 6 diseases
    disease_Pepper_Bell.pth   — diseases
    disease_Potato.pth        — diseases
    disease_Tomato.pth        — 8 diseases (val_acc ~90.8%)

Contract:
    Input:  context["_disease_model_cfg"]  — {path, labels, arch} set by router
            context["image"]["leaf_crop"]  — numpy BGR array
    Output: context["disease"]["label"]        — e.g. "Early Blight"
            context["disease"]["confidence"]   — float 0-1
            context["disease"]["all_probs"]    — full probability dict
            context["disease"]["model_used"]   — already set by router
            context["status"]["disease_classification"] — "completed" | "failed" | "skipped"
"""

from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch
import albumentations as A
from albumentations.pytorch import ToTensorV2

from backend.utils.model_loader import load_efficientnet, DEVICE


_EVAL_TF = A.Compose([
    A.Resize(224, 224),
    A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ToTensorV2(),
])


def predict_disease(context: dict, config: dict[str, Any]) -> dict:
    """
    Run disease classification using the crop-specific EfficientNet-B2 model.

    Args:
        context: Shared pipeline context (decision engine must have run first).
        config:  Parsed config.yaml dict.

    Returns:
        Mutated context with disease fields populated.
    """
    # ── Guard: decision routing must have succeeded ────────────────────
    if context["status"]["decision_routing"] != "completed":
        context["status"]["disease_classification"] = "skipped"
        return context

    model_cfg = context.pop("_disease_model_cfg", None)
    if model_cfg is None:
        context["notes"].append("Disease model config missing from context (internal error).")
        context["status"]["disease_classification"] = "failed"
        return context

    # ── Resolve model paths from config ───────────────────────────────
    base_dir = Path(__file__).resolve().parent.parent.parent.parent  # project root (Smart-Farming/)
    model_path = base_dir / model_cfg["path"]
    labels_path = base_dir / model_cfg["labels"]
    arch = model_cfg.get("arch", "efficientnet_b2")

    # ── Load model (cached after first call) ───────────────────────────
    result = load_efficientnet(model_path, labels_path, arch)
    if result is None:
        context["notes"].append(
            f"Disease model not found at {model_path}. "
            "Skipping disease classification."
        )
        context["status"]["disease_classification"] = "failed"
        return context

    model, classes = result

    # ── Read image ─────────────────────────────────────────────────────
    image_bgr = context["image"].get("leaf_crop")

    if image_bgr is None:
        processed_path = context["image"].get("processed_path")
        if not processed_path:
            context["notes"].append("No processed image for disease classification.")
            context["status"]["disease_classification"] = "failed"
            return context
        image_bgr = cv2.imread(processed_path, cv2.IMREAD_COLOR)
        if image_bgr is None:
            context["notes"].append(f"Could not read processed image: {processed_path}")
            context["status"]["disease_classification"] = "failed"
            return context

    # ── Run Inference ──────────────────────────────────────────────────
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    tensor = _EVAL_TF(image=image_rgb)["image"].unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        probs = torch.softmax(model(tensor), dim=1)[0].cpu().numpy()

    top_idx = int(np.argmax(probs))
    label = classes[top_idx]
    confidence = float(probs[top_idx])
    all_probs = {classes[i]: float(probs[i]) for i in range(len(classes))}

    context["disease"]["label"] = label
    context["disease"]["confidence"] = confidence
    context["disease"]["all_probs"] = all_probs
    context["status"]["disease_classification"] = "completed"

    # ── Low confidence note ────────────────────────────────────────────
    threshold = config["thresholds"].get("disease_confidence", 0.60)
    if confidence < threshold:
        context["notes"].append(
            f"Disease confidence ({confidence:.2f}) is low — "
            "treat this prediction as tentative."
        )

    return context

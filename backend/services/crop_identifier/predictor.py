"""
predictor.py — Crop Identification Service (EfficientNet-B0)

Reads the processed leaf image from the context, runs it through the trained
EfficientNet-B0 crop classifier, and writes the result back.

Supported crops (as of v1 model):
    Cotton, Groundnut, Pepper Bell, Potato, Tomato

Contract:
    Input:  context["image"]["leaf_crop"]  — numpy BGR array (224×224)
            context["image"]["processed_path"]  — fallback if leaf_crop is None
    Output: context["crop"]["label"]       — e.g. "Tomato"
            context["crop"]["confidence"]  — float 0-1
            context["status"]["crop_identification"]  — "completed" | "failed"
"""

from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch
import albumentations as A
from albumentations.pytorch import ToTensorV2

from backend.utils.model_loader import load_efficientnet, DEVICE


# ── Albumentations evaluation transform (no augmentation) ─────────────────
_EVAL_TF = A.Compose([
    A.Resize(224, 224),
    A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ToTensorV2(),
])


def predict_crop(context: dict, config: dict[str, Any]) -> dict:
    """
    Run crop identification on the preprocessed leaf image.

    Args:
        context: Shared pipeline context.
        config:  Parsed config.yaml dict.

    Returns:
        Mutated context with crop fields populated.
    """
    # ── Guard: preprocessing must have succeeded ───────────────────────
    if context["status"]["preprocessing"] != "completed":
        context["status"]["crop_identification"] = "skipped"
        return context

    # ── Resolve paths from config ──────────────────────────────────────
    crop_cfg = config["models"]["crop_identifier"]

    # Resolve paths relative to the backend/ directory (or absolute).
    base_dir = Path(__file__).resolve().parent.parent.parent.parent  # project root (Smart-Farming/)
    model_path = base_dir / crop_cfg["path"]
    labels_path = base_dir / crop_cfg["labels"]
    arch = crop_cfg.get("arch", "efficientnet_b0")

    # ── Load model (cached after first call) ───────────────────────────
    result = load_efficientnet(model_path, labels_path, arch)
    if result is None:
        context["notes"].append(
            f"Crop identifier model not found at {model_path}."
        )
        context["status"]["crop_identification"] = "failed"
        return context

    model, classes = result

    # ── Read image ─────────────────────────────────────────────────────
    image_bgr = context["image"].get("leaf_crop")

    if image_bgr is None:
        # Fallback: load from disk if in-memory array is missing
        processed_path = context["image"].get("processed_path")
        if not processed_path:
            context["notes"].append("No processed image available for crop identification.")
            context["status"]["crop_identification"] = "failed"
            return context
        image_bgr = cv2.imread(processed_path, cv2.IMREAD_COLOR)
        if image_bgr is None:
            context["notes"].append(f"Could not read processed image: {processed_path}")
            context["status"]["crop_identification"] = "failed"
            return context

    # ── Run Inference ──────────────────────────────────────────────────
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    label, confidence, all_probs = _run_inference(model, classes, image_rgb)

    context["crop"]["label"] = label
    context["crop"]["confidence"] = confidence
    context["status"]["crop_identification"] = "completed"

    # ── Confidence floor check ─────────────────────────────────────────
    threshold = config["thresholds"].get("crop_confidence", 0.75)
    if confidence < threshold:
        context["notes"].append(
            f"Crop confidence ({confidence:.2f}) is below threshold ({threshold}). "
            "Consider uploading a clearer photo."
        )

    return context


# ── Shared inference helper ────────────────────────────────────────────────

def _run_inference(
    model: torch.nn.Module,
    classes: list,
    image_rgb: np.ndarray,
) -> tuple[str, float, dict]:
    """
    Run a single image through a timm model and return (label, confidence, all_probs).

    Args:
        model:     Loaded, eval()-mode timm model.
        classes:   List of class name strings matching the model's output indices.
        image_rgb: Input image in RGB format (numpy array, any size).

    Returns:
        (top_label, top_confidence, {class_name: probability})
    """
    tensor = _EVAL_TF(image=image_rgb)["image"].unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        probs = torch.softmax(model(tensor), dim=1)[0].cpu().numpy()

    top_idx = int(np.argmax(probs))
    top_label = classes[top_idx]
    top_confidence = float(probs[top_idx])
    all_probs = {classes[i]: float(probs[i]) for i in range(len(classes))}

    return top_label, top_confidence, all_probs

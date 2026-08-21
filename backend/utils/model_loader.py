"""
model_loader.py — Shared model loading utilities with an in-memory cache.

Every service calls load_efficientnet() or load_yolo() here instead of
managing its own model loading.  The cache ensures a model is only loaded
from disk once, even if multiple requests come in simultaneously.
"""

import json
from pathlib import Path
from typing import Optional, Tuple

import torch
import timm

# ---------------------------------------------------------------------------
# Global in-memory model cache  {model_path_str: (model, classes)}
# ---------------------------------------------------------------------------
_model_cache: dict = {}

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def load_efficientnet(
    model_path: str | Path,
    labels_path: str | Path,
    arch: str,
    device: str = DEVICE,
) -> Optional[Tuple[torch.nn.Module, list]]:
    """
    Load a timm EfficientNet model + its class labels from disk.

    Returns (model, classes) or None if either file is missing.
    Results are cached by model_path so the file is only loaded once.
    """
    model_path = Path(model_path)
    labels_path = Path(labels_path)
    cache_key = str(model_path)

    if cache_key in _model_cache:
        return _model_cache[cache_key]

    if not model_path.exists():
        print(f"[ModelLoader] Model file not found: {model_path}")
        return None
    if not labels_path.exists():
        print(f"[ModelLoader] Labels file not found: {labels_path}")
        return None

    with open(labels_path, "r", encoding="utf-8") as f:
        classes = json.load(f)

    model = timm.create_model(arch, pretrained=False, num_classes=len(classes))
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    _model_cache[cache_key] = (model, classes)
    print(f"[ModelLoader] Loaded '{arch}' from {model_path.name} ({len(classes)} classes) on {device}")
    return _model_cache[cache_key]


def load_yolo(model_path: str | Path):
    """
    Load an Ultralytics YOLO model from disk.

    Returns the YOLO model or None if the file is missing.
    Results are cached by model_path.
    """
    model_path = Path(model_path)
    cache_key = str(model_path)

    if cache_key in _model_cache:
        return _model_cache[cache_key]

    if not model_path.exists():
        print(f"[ModelLoader] YOLO model file not found: {model_path}")
        return None

    try:
        from ultralytics import YOLO
        model = YOLO(str(model_path))
        _model_cache[cache_key] = model
        print(f"[ModelLoader] Loaded YOLO model from {model_path.name}")
        return model
    except ImportError:
        print("[ModelLoader] ultralytics not installed. Pest detection unavailable.")
        return None


def clear_cache() -> None:
    """Clear the model cache (useful for testing)."""
    _model_cache.clear()

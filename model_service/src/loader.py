"""
loader.py — Model loading utilities with in-memory cache for model_service.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional, Tuple, Any

import torch
import timm

logger = logging.getLogger(__name__)

_model_cache: dict[str, Any] = {}

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
SERVICE_ROOT = Path(__file__).resolve().parent.parent

# Fallback class labels in case disk read or Git LFS issues occur
FALLBACK_LABELS: dict[str, list[str]] = {
    "crop_identifier": ["Cotton", "Groundnut", "Pepper Bell", "Potato", "Tomato"],
    "disease_Tomato": ["Bacterial Spot", "Early Blight", "Healthy", "Late Blight", "Mold Leaf", "Mosaic Virus", "Septoria", "Yellow Curl Virus"],
    "disease_Cotton": ["Alternaria Leaf Spot", "Bacterial Blight", "Curl Virus", "Fusarium Wilt", "Healthy", "Powdery Mildew", "Target Spot", "Verticillium Wilt"],
    "disease_Groundnut": ["Althernaria Leaf Spot", "Healthy", "Leaf Spot", "Nutrition Deficiency", "Rosette", "Rust"],
    "disease_Pepper_Bell": ["Bacterial Spot", "Cercospora Leaf Spot", "Edema", "Healthy", "Leaf Curl", "Nutrition Deficiency", "Powdery Mildew"],
    "disease_Potato": ["Bacteria", "Early Blight", "Fungi", "Healthy", "Late Blight", "Nematode", "Pest", "Virus"],
}


def resolve_model_path(rel_or_abs_path: str | Path) -> Path:
    p = Path(rel_or_abs_path)
    return p if p.is_absolute() else (SERVICE_ROOT / p).resolve()


def is_git_lfs_pointer(path: Path) -> bool:
    """Check if file is a Git LFS pointer text file instead of real content."""
    if not path.is_file():
        return False
    try:
        if path.stat().st_size < 1024:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                prefix = f.read(50)
                if prefix.startswith("version https://git-lfs"):
                    return True
    except Exception:
        pass
    return False


def _get_fallback_labels(labels_path: Path) -> Optional[list[str]]:
    fname = labels_path.stem
    for key, labels in FALLBACK_LABELS.items():
        if key in fname:
            return labels
    return None


def load_efficientnet(
    model_path: str | Path,
    labels_path: str | Path,
    arch: str,
    device: str = DEVICE,
) -> Optional[Tuple[torch.nn.Module, list]]:
    """
    Load a timm EfficientNet model + its class labels from disk.
    Returns (model, classes) or None if either file is missing or invalid.
    Results are cached by model_path.
    """
    model_path = resolve_model_path(model_path)
    labels_path = resolve_model_path(labels_path)
    cache_key = str(model_path)

    if cache_key in _model_cache:
        return _model_cache[cache_key]

    if not model_path.exists():
        logger.error(f"[ModelLoader] Model file not found: {model_path}")
        return None

    if is_git_lfs_pointer(model_path):
        logger.error(f"[ModelLoader] Model file is a Git LFS pointer text file, not binary weights: {model_path}")
        return None

    classes = None
    if labels_path.exists() and not is_git_lfs_pointer(labels_path):
        try:
            with open(labels_path, "r", encoding="utf-8") as f:
                classes = json.load(f)
        except Exception as exc:
            logger.warning(f"[ModelLoader] Failed to parse labels from {labels_path}: {exc}. Checking fallback...")
            classes = _get_fallback_labels(labels_path)
    else:
        logger.warning(f"[ModelLoader] Labels file {labels_path} missing or LFS pointer. Checking fallback...")
        classes = _get_fallback_labels(labels_path)

    if not classes:
        logger.error(f"[ModelLoader] Could not resolve classes for {labels_path}")
        return None

    try:
        model = timm.create_model(arch, pretrained=False, num_classes=len(classes))
        model.load_state_dict(torch.load(model_path, map_location=device, weights_only=False))
        model.to(device)
        model.eval()

        _model_cache[cache_key] = (model, classes)
        logger.info(f"[ModelLoader] Loaded '{arch}' from {model_path.name} ({len(classes)} classes) on {device}")
        return _model_cache[cache_key]
    except Exception as exc:
        logger.error(f"[ModelLoader] Failed loading model {model_path}: {exc}", exc_info=True)
        return None


def load_yolo(model_path: str | Path):
    """
    Load an Ultralytics YOLO model from disk.
    Returns the YOLO model or None if the file is missing or invalid.
    """
    model_path = resolve_model_path(model_path)
    cache_key = str(model_path)

    if cache_key in _model_cache:
        return _model_cache[cache_key]

    if not model_path.exists():
        logger.error(f"[ModelLoader] YOLO model file not found: {model_path}")
        return None

    if is_git_lfs_pointer(model_path):
        logger.error(f"[ModelLoader] YOLO file is a Git LFS pointer text file: {model_path}")
        return None

    try:
        from ultralytics import YOLO
        model = YOLO(str(model_path))
        _model_cache[cache_key] = model
        logger.info(f"[ModelLoader] Loaded YOLO model from {model_path.name}")
        return model
    except ImportError:
        logger.warning("[ModelLoader] ultralytics not installed. Pest detection unavailable.")
        return None
    except Exception as exc:
        logger.error(f"[ModelLoader] Failed loading YOLO model from {model_path}: {exc}", exc_info=True)
        return None


def clear_cache() -> None:
    _model_cache.clear()


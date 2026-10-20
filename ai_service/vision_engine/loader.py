"""
loader.py — Model loading utilities with LRU in-memory cache and ONNX int8 support.
"""

from __future__ import annotations

import gc
import json
import logging
from collections import OrderedDict
from pathlib import Path
from typing import Optional, Tuple, Any

import torch
import timm

logger = logging.getLogger(__name__)

# Permanent cache for models required on every request (e.g. crop_identifier)
_persistent_model_cache: dict[str, Any] = {}

# In-memory LRU cache for per-crop disease models (limits memory on free-tier 2 vCPU / 16GB / Render 512MB)
MAX_DISEASE_MODELS = 2
_disease_model_lru: OrderedDict[str, Any] = OrderedDict()

try:
    from core.config import settings
    DEVICE = settings.DEVICE
except Exception:
    DEVICE = "cpu"

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


class ONNXModelWrapper:
    """Wrapper that adapts ONNX Runtime InferenceSession to PyTorch callable interface."""

    def __init__(self, session_path: str):
        import onnxruntime as ort
        self.session = ort.InferenceSession(session_path, providers=["CPUExecutionProvider"])
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.path = session_path

    def __call__(self, tensor: torch.Tensor) -> torch.Tensor:
        arr = tensor.detach().cpu().numpy()
        preds = self.session.run([self.output_name], {self.input_name: arr})[0]
        return torch.from_numpy(preds)

    def to(self, device: str) -> "ONNXModelWrapper":
        return self

    def eval(self) -> "ONNXModelWrapper":
        return self


def resolve_model_path(rel_or_abs_path: str | Path) -> Path:
    p = Path(rel_or_abs_path)
    if p.is_absolute() and p.exists():
        return p
    target = (SERVICE_ROOT / p).resolve()
    if target.exists():
        return target
    sub_target = (SERVICE_ROOT / "models" / p.name).resolve()
    if sub_target.exists():
        return sub_target
    return target


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


def _find_onnx_candidate(model_path: Path) -> Optional[Path]:
    """Check if an int8 or fp32 ONNX model is available beside the PyTorch checkpoint."""
    if model_path.suffix.lower() == ".onnx" and model_path.exists():
        return model_path

    # Check for quantized int8 ONNX first
    int8_candidate = model_path.with_name(f"{model_path.stem}_int8.onnx")
    if int8_candidate.exists():
        return int8_candidate

    # Check for standard ONNX
    onnx_candidate = model_path.with_suffix(".onnx")
    if onnx_candidate.exists():
        return onnx_candidate

    return None


def load_efficientnet(
    model_path: str | Path,
    labels_path: str | Path,
    arch: str,
    device: str = DEVICE,
) -> Optional[Tuple[Any, list]]:
    """
    Load an EfficientNet model (ONNX int8 if available, otherwise PyTorch timm) + class labels.
    Uses persistent caching for crop_identifier, and an LRU cache (maxsize=2) for disease models
    to stay well within free-tier memory quotas.
    """
    model_path = resolve_model_path(model_path)
    labels_path = resolve_model_path(labels_path)
    cache_key = str(model_path)

    is_crop_model = "crop_identifier" in cache_key or "crop" in model_path.stem.lower()

    if is_crop_model:
        if cache_key in _persistent_model_cache:
            return _persistent_model_cache[cache_key]
    else:
        if cache_key in _disease_model_lru:
            _disease_model_lru.move_to_end(cache_key)
            return _disease_model_lru[cache_key]

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

    # Try loading ONNX model first for 2-3x speed and 75% RAM savings
    onnx_file = _find_onnx_candidate(model_path)
    if onnx_file:
        try:
            model = ONNXModelWrapper(str(onnx_file))
            logger.info(f"[ModelLoader] Loaded ONNX session from {onnx_file.name} ({len(classes)} classes)")
            entry = (model, classes)
            if is_crop_model:
                _persistent_model_cache[cache_key] = entry
            else:
                _store_in_disease_lru(cache_key, entry)
            return entry
        except Exception as exc:
            logger.warning(f"[ModelLoader] Could not load ONNX session from {onnx_file}: {exc}. Falling back to PyTorch.")

    # PyTorch timm model loading
    try:
        model = timm.create_model(arch, pretrained=False, num_classes=len(classes))
        model.load_state_dict(torch.load(model_path, map_location=device, weights_only=False))
        model.to(device)
        model.eval()

        entry = (model, classes)
        if is_crop_model:
            _persistent_model_cache[cache_key] = entry
            logger.info(f"[ModelLoader] Loaded permanent crop model '{arch}' from {model_path.name} on {device}")
        else:
            _store_in_disease_lru(cache_key, entry)
            logger.info(f"[ModelLoader] Loaded disease model '{arch}' into LRU from {model_path.name} on {device}")
        return entry
    except Exception as exc:
        logger.error(f"[ModelLoader] Failed loading model {model_path}: {exc}", exc_info=True)
        return None


def _store_in_disease_lru(key: str, entry: Any) -> None:
    if key in _disease_model_lru:
        _disease_model_lru.move_to_end(key)
    else:
        if len(_disease_model_lru) >= MAX_DISEASE_MODELS:
            evicted_key, _ = _disease_model_lru.popitem(last=False)
            logger.info(f"[ModelLoader] LRU eviction: unloaded disease model '{Path(evicted_key).name}' to conserve RAM budget.")
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
        _disease_model_lru[key] = entry


def load_yolo(model_path: str | Path):
    """
    Load an Ultralytics YOLO model from disk.
    Returns the YOLO model or None if the file is missing or invalid.
    """
    model_path = resolve_model_path(model_path)
    cache_key = str(model_path)

    if cache_key in _persistent_model_cache:
        return _persistent_model_cache[cache_key]

    if not model_path.exists():
        logger.error(f"[ModelLoader] YOLO model file not found: {model_path}")
        return None

    if is_git_lfs_pointer(model_path):
        logger.error(f"[ModelLoader] YOLO file is a Git LFS pointer text file: {model_path}")
        return None

    try:
        from ultralytics import YOLO
        model = YOLO(str(model_path))
        _persistent_model_cache[cache_key] = model
        logger.info(f"[ModelLoader] Loaded YOLO model from {model_path.name}")
        return model
    except ImportError:
        logger.warning("[ModelLoader] ultralytics not installed. Pest detection unavailable.")
        return None
    except Exception as exc:
        logger.error(f"[ModelLoader] Failed loading YOLO model from {model_path}: {exc}", exc_info=True)
        return None


def get_cache_stats() -> dict[str, Any]:
    """Return memory and cache diagnostic statistics."""
    return {
        "persistent_models": list(_persistent_model_cache.keys()),
        "lru_disease_models": list(_disease_model_lru.keys()),
        "max_disease_models": MAX_DISEASE_MODELS,
    }


def clear_cache() -> None:
    _persistent_model_cache.clear()
    _disease_model_lru.clear()
    gc.collect()

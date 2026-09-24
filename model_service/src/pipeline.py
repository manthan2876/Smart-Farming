"""
pipeline.py — Pure Computer Vision Pipeline Orchestrator for model_service
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any
import yaml
import numpy as np

from src.stages.preprocessing import OpenCVPreprocessorService
from src.stages.crop_identifier import predict_crop
from src.stages.decision_router import route_to_disease_model
from src.stages.disease_classifier import predict_disease
from src.stages.severity import estimate_severity
from src.stages.pest_detector import predict_pest

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


def load_config() -> dict[str, Any]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


_CONFIG = load_config()
_PREPROCESSOR = OpenCVPreprocessorService(_CONFIG)


def _init_context(image_bgr: np.ndarray, filename: str) -> dict[str, Any]:
    return {
        "filename": filename,
        "image_bgr": image_bgr,
        "image": {
            "blur_score": None,
            "brightness_score": None,
            "quality_score": None,
            "leaf_detected": False,
        },
        "crop": {
            "label": None,
            "confidence": None,
            "uncertainty": None,
            "confidence_rating": None,
            "status": None,
            "is_uncertain": False,
            "model_name": None,
            "model_version": None,
            "model_file": None,
        },
        "disease": {
            "label": None,
            "confidence": None,
            "uncertainty": None,
            "confidence_rating": None,
            "is_uncertain": False,
            "model_name": None,
            "model_version": None,
            "model_used": None,
            "all_probs": None,
        },
        "severity": {
            "percent": None,
            "affected_area": None,
            "bucket": None,
        },
        "pests": [],
        "pest_classification": {
            "model_type": "classification",
            "model_name": None,
            "model_used": None,
            "status": None,
            "available": False,
        },
        "status": {
            "preprocessing": "pending",
            "crop_identification": "pending",
            "decision_routing": "pending",
            "disease_classification": "pending",
            "severity": "pending",
            "pest_detection": "pending",
        },
        "notes": [],
        "stages": {},
    }


def run_vision_pipeline(image_bgr: np.ndarray, filename: str = "upload.jpg") -> dict[str, Any]:
    context = _init_context(image_bgr, filename)
    t0_total = time.perf_counter()

    def _exec_stage(stage_name: str, fn, *args, **kwargs):
        t0 = time.perf_counter()
        context["status"][stage_name] = "processing"
        res = fn(*args, **kwargs)
        duration_ms = round((time.perf_counter() - t0) * 1000)
        curr_status = context["status"].get(stage_name, "processing")
        if curr_status == "processing":
            context["status"][stage_name] = "completed"
        context["stages"][stage_name] = {
            "status": context["status"][stage_name],
            "duration_ms": duration_ms,
        }
        return res

    # 1. Preprocessing
    context = _exec_stage("preprocessing", _PREPROCESSOR.process, context)
    if context["status"]["preprocessing"] != "completed":
        # Formulate human error message
        err_msg = "Image validation failed."
        prep_status = context["status"]["preprocessing"]
        if prep_status == "failed_blur":
            blur = context["image"].get("blur_score", 0.0)
            err_msg = f"Image is too blurry (sharpness score: {blur:.1f}). Please hold camera steady."
        elif prep_status == "failed_lighting":
            bright = context["image"].get("brightness_score", 0.0)
            err_msg = f"Lighting is poor (brightness: {bright:.1f}). Please capture in balanced daylight."
        elif prep_status == "failed_no_leaf":
            err_msg = "No crop leaf was detected. Please ensure leaf is in the center of the frame."

        context["error_message"] = err_msg
        _clean_context_for_response(context)
        return context

    # 2. Crop Identification
    context = _exec_stage("crop_identification", predict_crop, context, _CONFIG)

    # 3. Decision Routing
    context = _exec_stage("decision_routing", route_to_disease_model, context, _CONFIG)

    # 4. Disease Classification
    context = _exec_stage("disease_classification", predict_disease, context, _CONFIG)

    # 5. Severity Estimation
    context = _exec_stage("severity", estimate_severity, context)

    # 6. Pest Detection
    context = _exec_stage("pest_detection", predict_pest, context, _CONFIG)

    total_duration_ms = round((time.perf_counter() - t0_total) * 1000)
    context["stages"]["total_vision_duration_ms"] = total_duration_ms

    return _clean_context_for_response(context)


def _clean_context_for_response(context: dict) -> dict:
    """Remove in-memory binary/numpy arrays before JSON serialization."""
    context.pop("image_bgr", None)
    if "leaf_crop" in context.get("image", {}):
        context["image"].pop("leaf_crop", None)
    context.pop("_disease_model_cfg", None)
    return context

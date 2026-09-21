"""
pipeline.py — Pipeline Orchestrator
"""

import sys
from pathlib import Path
from typing import Any
import yaml
from app.core.config import settings

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.preprocessing.service import OpenCVPreprocessorService
from app.services.crop_identifier.predictor import predict_crop
from app.services.decision_engine.router import route_to_disease_model
from app.services.disease_classifier.predictor import predict_disease
from app.services.severity.estimator import estimate_severity
from app.services.pest_detector.predictor import predict_pest
from app.services.weather.service import fetch_weather
from app.services.recommendation.service import generate_recommendation

def _find_config_path() -> Path:
    return settings.CONFIG_PATH


_CONFIG_PATH = _find_config_path()


def _load_config(config_path: Path | None = None) -> dict[str, Any]:
    target = config_path or _find_config_path()
    with open(target, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)



_CONFIG: dict[str, Any] = _load_config()
_PREPROCESSOR = OpenCVPreprocessorService(_CONFIG)


import time
from datetime import datetime, timezone

def run_pipeline(context: dict) -> dict:
    if "stages" not in context:
        context["stages"] = {}
    if "status" not in context:
        context["status"] = {}

    pipeline_start = time.perf_counter()

    def _exec_stage(stage_name: str, fn, *args, **kwargs):
        t0 = time.perf_counter()
        now_iso = datetime.now(timezone.utc).isoformat()
        context["status"][stage_name] = "processing"
        context["stages"][stage_name] = {
            "status": "processing",
            "started_at": now_iso,
            "completed_at": None,
            "duration_ms": None,
        }
        res = fn(*args, **kwargs)
        duration_ms = round((time.perf_counter() - t0) * 1000)
        context["status"][stage_name] = "completed"
        context["stages"][stage_name].update({
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "duration_ms": duration_ms,
        })
        return res

    context = _exec_stage("preprocessing", _PREPROCESSOR.process, context)
    if context["status"]["preprocessing"] != "completed":
        context["status"]["pipeline"] = "failed"
        return context

    context = _exec_stage("crop_identification", predict_crop, context, _CONFIG)
    context = _exec_stage("decision_routing", route_to_disease_model, context, _CONFIG)
    context = _exec_stage("disease_classification", predict_disease, context, _CONFIG)
    context = _exec_stage("severity", estimate_severity, context)
    context = _exec_stage("pest_detection", predict_pest, context, _CONFIG)
    context = _exec_stage("weather", fetch_weather, context, _CONFIG)
    context = _exec_stage("recommendation", generate_recommendation, context, _CONFIG)

    total_duration_ms = round((time.perf_counter() - pipeline_start) * 1000)
    context["status"]["pipeline"] = "completed"
    context["stages"]["pipeline"] = {
        "status": "completed",
        "message": "Pipeline completed successfully.",
        "duration_ms": total_duration_ms,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    SCHEMA_VERSION = "2.0.0"
    context["schema_version"] = SCHEMA_VERSION
    thresholds = _CONFIG.get("thresholds", {})
    context["provenance"] = {
        "schema_version": SCHEMA_VERSION,
        "config": {
            "version": "1.0.0",
            "thresholds": {
                "crop_confidence": thresholds.get("crop_confidence", settings.CROP_CONFIDENCE_THRESHOLD),
                "disease_confidence": thresholds.get("disease_confidence", settings.DISEASE_CONFIDENCE_THRESHOLD),
            },
        },
        "models": {
            "crop": {
                "name": context.get("crop", {}).get("model_name", "EfficientNet-B0"),
                "version": context.get("crop", {}).get("model_version", "v1.0"),
                "model_file": context.get("crop", {}).get("model_file", "crop_identifier_v1.pth"),
            },
            "disease": {
                "name": context.get("disease", {}).get("model_name", "EfficientNet-B2"),
                "version": context.get("disease", {}).get("model_version", "v1.0"),
                "model_file": context.get("disease", {}).get("model_used") or "default",
            },
            "severity": {
                "name": "HSV Contour Heuristic",
                "version": "v1.0",
            },
            "pest": {
                "name": context.get("pest_classification", {}).get("model_name", "YOLO Pest Classifier"),
                "version": context.get("pest_classification", {}).get("version", "v1.0"),
                "model_file": context.get("pest_classification", {}).get("model_used") or "pest_classifier/weights/best.pt",
                "available": context.get("pest_classification", {}).get("available", context.get("status", {}).get("pest_detection") == "completed"),
            },
        },
        "weather_provider": {
            "provider": context.get("weather", {}).get("provider", "OpenWeatherMap"),
            "status": context.get("weather", {}).get("status", "unknown"),
            "is_degraded": context.get("weather", {}).get("is_degraded", False),
            "timestamp": context.get("weather", {}).get("timestamp"),
        },
        "recommendation_provider": {
            "provider": context.get("recommendation", {}).get("provider", "HuggingFace / nscale"),
            "model": context.get("recommendation", {}).get("model", "Qwen/Qwen3-4B-Instruct-2507"),
            "prompt_version": context.get("recommendation", {}).get("prompt_version", "v1.0"),
            "is_fallback": context.get("recommendation", {}).get("is_fallback", False),
            "fallback_reason": context.get("recommendation", {}).get("fallback_reason"),
        },
        "pipeline_duration_ms": total_duration_ms,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    return context


def reload_config() -> None:
    global _CONFIG, _PREPROCESSOR
    _CONFIG = _load_config()
    _PREPROCESSOR = OpenCVPreprocessorService(_CONFIG)
    print("[Pipeline] Config reloaded from", _CONFIG_PATH)

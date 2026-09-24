"""
pipeline.py — Pipeline Orchestrator

Two consumers share this module:
  * ``run_pipeline``           – synchronous, single-call orchestration (no live events).
  * ``services/prediction_job`` – the ARQ worker path, which calls the stage functions itself so
                                  it can publish live progress events. It reuses ``SCHEMA_VERSION``
                                  and ``build_provenance`` from here so the two never drift apart.
"""

from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# Must run before any ``app.*`` import when this file is executed as a script.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.services.model_client import execute_remote_vision_pipeline
from app.services.weather.service import fetch_weather
from app.services.recommendation.service import generate_recommendation

SCHEMA_VERSION = "2.0.0"


def _find_config_path() -> Path:
    return settings.CONFIG_PATH


_CONFIG_PATH = _find_config_path()


def _load_config(config_path: Path | None = None) -> dict[str, Any]:
    target = config_path or _find_config_path()
    with open(target, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


_CONFIG: dict[str, Any] = _load_config()


def build_provenance(context: dict, total_duration_ms: int) -> dict[str, Any]:
    """Build the provenance block stored with every finished prediction.

    Shared by ``run_pipeline`` and the ARQ worker job so both produce identical metadata.
    Reads the *current* module-level ``_CONFIG`` so it honours ``reload_config()``.
    """
    thresholds = _CONFIG.get("thresholds", {})
    crop = context.get("crop", {}) or {}
    disease = context.get("disease", {}) or {}
    pest = context.get("pest_classification", {}) or {}
    weather = context.get("weather", {}) or {}
    recommendation = context.get("recommendation", {}) or {}

    return {
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
                "name": crop.get("model_name", "EfficientNet-B0"),
                "version": crop.get("model_version", "v1.0"),
                "model_file": crop.get("model_file", "crop_identifier_v1.pth"),
            },
            "disease": {
                "name": disease.get("model_name", "EfficientNet-B2"),
                "version": disease.get("model_version", "v1.0"),
                "model_file": disease.get("model_used") or "default",
            },
            "severity": {
                "name": "HSV Contour Heuristic",
                "version": "v1.0",
            },
            "pest": {
                "name": pest.get("model_name", "YOLO Pest Classifier"),
                "version": pest.get("version", "v1.0"),
                "model_file": pest.get("model_used") or "pest_classifier/weights/best.pt",
                "available": pest.get(
                    "available",
                    context.get("status", {}).get("pest_detection") == "completed",
                ),
            },
        },
        "weather_provider": {
            "provider": weather.get("provider", "OpenWeatherMap"),
            "status": weather.get("status", "unknown"),
            "is_degraded": weather.get("is_degraded", False),
            "timestamp": weather.get("timestamp"),
        },
        "recommendation_provider": {
            "provider": recommendation.get("provider", "HuggingFace / nscale"),
            "model": recommendation.get("model", "Qwen/Qwen3-4B-Instruct-2507"),
            "prompt_version": recommendation.get("prompt_version", "v1.0"),
            "is_fallback": recommendation.get("is_fallback", False),
            "fallback_reason": recommendation.get("fallback_reason"),
        },
        "pipeline_duration_ms": total_duration_ms,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


async def run_pipeline(
    context: dict,
    image_bytes: bytes,
    filename: str = "upload.jpg",
    content_type: str = "image/jpeg",
) -> dict:
    if "stages" not in context:
        context["stages"] = {}
    if "status" not in context:
        context["status"] = {}
    context["status"].setdefault("pipeline", "processing")

    pipeline_start = time.perf_counter()

    # 1. Computer Vision stages executed remotely on Server 2 (model_service)
    context = await execute_remote_vision_pipeline(context, image_bytes, filename, content_type)

    # 2. Weather
    context = fetch_weather(context, _CONFIG)

    # 3. LLM Recommendation
    context = generate_recommendation(context, _CONFIG)

    total_duration_ms = round((time.perf_counter() - pipeline_start) * 1000)
    context["status"]["pipeline"] = "completed"
    context["stages"]["pipeline"] = {
        "status": "completed",
        "message": "Pipeline completed successfully.",
        "duration_ms": total_duration_ms,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    context["schema_version"] = SCHEMA_VERSION
    context["provenance"] = build_provenance(context, total_duration_ms)

    return context


def reload_config() -> None:
    """Reload config."""
    global _CONFIG
    _CONFIG = _load_config()
    print("[Pipeline] Config reloaded from", _CONFIG_PATH)
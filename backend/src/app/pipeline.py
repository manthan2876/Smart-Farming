"""
pipeline.py — Pipeline Orchestrator
"""

import sys
from pathlib import Path
from typing import Any
import yaml

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

_CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"


def _load_config(config_path: Path = _CONFIG_PATH) -> dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


_CONFIG: dict[str, Any] = _load_config()
_PREPROCESSOR = OpenCVPreprocessorService(_CONFIG)


def run_pipeline(context: dict) -> dict:
    context = _PREPROCESSOR.process(context)
    if context["status"]["preprocessing"] != "completed":
        return context

    context = predict_crop(context, _CONFIG)
    context = route_to_disease_model(context, _CONFIG)
    context = predict_disease(context, _CONFIG)
    context = estimate_severity(context)
    context = predict_pest(context, _CONFIG)
    context = fetch_weather(context, _CONFIG)
    context = generate_recommendation(context, _CONFIG)

    return context


def reload_config() -> None:
    global _CONFIG, _PREPROCESSOR
    _CONFIG = _load_config()
    _PREPROCESSOR = OpenCVPreprocessorService(_CONFIG)
    print("[Pipeline] Config reloaded from", _CONFIG_PATH)

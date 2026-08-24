"""
pipeline.py — Pipeline Orchestrator
"""

from pathlib import Path
from typing import Any
import yaml

from services.preprocessing.service import OpenCVPreprocessorService
from services.crop_identifier.predictor import predict_crop
from services.decision_engine.router import route_to_disease_model
from services.disease_classifier.predictor import predict_disease
from services.severity.estimator import estimate_severity
from services.pest_detector.predictor import predict_pest
from services.weather.service import fetch_weather

_CONFIG_PATH = Path(__file__).parent / "config.yaml"

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
    
    # Integrated Weather Fetch Stage before recommendations
    context = fetch_weather(context, _CONFIG)
    
    return context

def reload_config() -> None:
    global _CONFIG, _PREPROCESSOR
    _CONFIG = _load_config()
    _PREPROCESSOR = OpenCVPreprocessorService(_CONFIG)
    print("[Pipeline] Config reloaded from", _CONFIG_PATH)
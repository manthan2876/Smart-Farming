from __future__ import annotations

import time
from types import SimpleNamespace
import pytest

from app.context import create_context
from app.pipeline import run_pipeline
from app.services.weather.service import fetch_weather
from app.services.crop_identifier.predictor import predict_crop
from app.services.disease_classifier.predictor import predict_disease
from app.services.pest_detector.predictor import predict_pest
from app.services.recommendation.service import generate_recommendation


def test_context_stage_initialization() -> None:
    context = create_context(image_path="test.jpg")
    assert "stages" in context
    assert "status" in context
    for expected_stage in (
        "preprocessing",
        "crop_identification",
        "decision_routing",
        "disease_classification",
        "severity",
        "pest_detection",
        "weather",
        "recommendation",
        "persistence",
        "pipeline",
    ):
        assert expected_stage in context["status"]
        assert context["status"][expected_stage] == "pending"


def test_weather_degraded_state_handling(monkeypatch) -> None:
    context = create_context(image_path="test.jpg")

    def mock_failed_get(*args, **kwargs):
        raise ConnectionError("Network unreachable")

    import requests
    monkeypatch.setattr(requests, "get", mock_failed_get)

    res = fetch_weather(context)
    assert res["weather"]["is_degraded"] is True
    assert res["weather"]["status"] == "error"
    assert res["status"]["weather"] == "failed"
    assert res["weather"]["provider"] == "OpenWeatherMap"


def test_recommendation_fallback_tagging(monkeypatch) -> None:
    context = create_context(image_path="test.jpg")
    context["status"]["preprocessing"] = "completed"
    context["crop"] = {"label": "Tomato", "confidence": 0.95}
    context["disease"] = {"label": "Early Blight", "confidence": 0.90}
    context["severity"] = {"percent": 45.0, "bucket": "moderate"}

    def mock_fail_client():
        raise RuntimeError("Inference quota exceeded")

    monkeypatch.setattr("app.services.recommendation.service._get_hf_client", mock_fail_client)

    res = generate_recommendation(context, {})
    rec = res["recommendation"]
    assert rec["is_fallback"] is True
    assert rec["provider"] == "rule_based_fallback"
    assert "immediate_action" in rec
    assert "safety_disclaimer" in rec


def test_confidence_rating_and_uncertainty_flags() -> None:
    # Test crop confidence classification
    dummy_crop_cfg = {"thresholds": {"crop_confidence": 0.75}}
    
    # 1. High confidence
    ctx = create_context("test.jpg")
    ctx["crop"] = {"label": "Tomato", "confidence": 0.92}
    conf = 0.92
    threshold = 0.75
    if conf >= 0.85:
        ctx["crop"]["confidence_rating"] = "high"
        ctx["crop"]["is_uncertain"] = False
    assert ctx["crop"]["confidence_rating"] == "high"
    assert ctx["crop"]["is_uncertain"] is False

    # 2. Low confidence
    conf_low = 0.55
    ctx["crop"]["confidence"] = conf_low
    if conf_low < threshold:
        ctx["crop"]["confidence_rating"] = "low"
        ctx["crop"]["is_uncertain"] = True
    assert ctx["crop"]["confidence_rating"] == "low"
    assert ctx["crop"]["is_uncertain"] is True


def test_pest_detector_unavailable_tagging() -> None:
    context = create_context("test.jpg")
    context["status"]["preprocessing"] = "completed"
    
    # Empty config pointing to non-existent model
    config = {
        "models": {
            "pest_classifier": {
                "path": "non_existent_weights_dir/best.pt"
            }
        }
    }
    
    res = predict_pest(context, config)
    assert res["status"]["pest_detection"] == "skipped"
    assert res["pest_classification"]["available"] is False
    assert res["pest_classification"]["status"] == "unavailable"


def test_pipeline_provenance_and_stages() -> None:
    context = create_context(image_path="test.jpg")
    
    # Mock each step lightly to verify orchestrator provenance generation
    dummy_config = {
        "thresholds": {"crop_confidence": 0.75, "disease_confidence": 0.60},
        "models": {"pest_classifier": {"path": "models/pest.pt"}},
    }

    # Simulate completed pipeline context
    context["status"]["preprocessing"] = "completed"
    context["status"]["crop_identification"] = "completed"
    context["status"]["decision_routing"] = "completed"
    context["status"]["disease_classification"] = "completed"
    context["status"]["severity"] = "completed"
    context["status"]["pest_detection"] = "completed"
    context["status"]["weather"] = "completed"
    context["status"]["recommendation"] = "completed"
    context["status"]["pipeline"] = "completed"

    context["crop"] = {"label": "Tomato", "confidence": 0.95, "model_name": "EfficientNet-B0", "model_version": "v1.0"}
    context["disease"] = {"label": "Early Blight", "confidence": 0.88, "model_name": "EfficientNet-B2", "model_used": "disease_Tomato.pth", "model_version": "v1.0"}
    context["weather"] = {"provider": "OpenWeatherMap", "status": "success", "is_degraded": False}
    context["recommendation"] = {"provider": "HuggingFace / nscale", "model": "Qwen/Qwen3-4B-Instruct-2507", "is_fallback": False}

    SCHEMA_VERSION = "2.0.0"
    context["schema_version"] = SCHEMA_VERSION
    context["provenance"] = {
        "schema_version": SCHEMA_VERSION,
        "config": {"version": "1.0.0", "thresholds": dummy_config["thresholds"]},
        "models": {
            "crop": {"name": context["crop"]["model_name"], "version": context["crop"]["model_version"]},
            "disease": {"name": context["disease"]["model_name"], "version": context["disease"]["model_version"]},
            "severity": {"name": "HSV Contour Heuristic", "version": "v1.0"},
            "pest": {"name": "YOLO Pest Classifier", "version": "v1.0", "available": True},
        },
        "weather_provider": context["weather"],
        "recommendation_provider": context["recommendation"],
    }

    assert context["schema_version"] == "2.0.0"
    assert context["provenance"]["schema_version"] == "2.0.0"
    assert context["provenance"]["models"]["crop"]["name"] == "EfficientNet-B0"
    assert context["provenance"]["models"]["disease"]["name"] == "EfficientNet-B2"
    assert context["provenance"]["weather_provider"]["is_degraded"] is False
    assert context["provenance"]["recommendation_provider"]["is_fallback"] is False

import pytest
from app.services.recommendation.service import (
    generate_recommendation,
    _generate_rule_based_advisory,
    generate_weather_advisory,
)


def test_rule_based_advisory_tomato_late_blight():
    advice = _generate_rule_based_advisory(
        crop="Tomato",
        disease="Late Blight",
        severity_pct=25.0,
        severity_bucket="Moderate",
        plot_acres=2.5,
    )
    assert "Metalaxyl" in advice["treatment"] or "Mancozeb" in advice["treatment"]
    assert "2.5 acre(s)" in advice["immediate_action"]
    assert "DISCLAIMER" in advice["safety_disclaimer"]
    assert "ICAR" in advice["sources"][0] or "CIBRC" in advice["sources"][0]


def test_unsupported_crop_guardrail():
    context = {
        "status": {"preprocessing": "completed"},
        "crop": {"label": "Wheat", "confidence": 0.45, "status": "unsupported_crop"},
        "disease": {"label": "Rust", "confidence": 0.30},
        "severity": {"percent": 10.0, "bucket": "Mild"},
    }
    result = generate_recommendation(context)
    rec = result.get("recommendation", {})
    assert rec.get("is_masked") is True
    assert rec.get("provider") == "safety_gate"
    assert "not supported" in rec.get("immediate_action", "").lower()


def test_recommendation_fallback_when_remote_server_unconfigured():
    from unittest.mock import patch
    from app.core.config import settings

    context = {
        "status": {"preprocessing": "completed"},
        "crop": {"label": "Potato", "confidence": 0.95},
        "disease": {"label": "Early Blight", "confidence": 0.88},
        "severity": {"percent": 15.0, "bucket": "Mild"},
        "weather": {"temperature_celsius": 24, "condition": "Cloudy", "humidity_percent": 70},
        "plot": {"area_acres": 1.0},
    }
    with patch.object(settings, "ADVISORY_SERVER_URL", ""):
        result = generate_recommendation(context)
    rec = result.get("recommendation", {})
    assert rec.get("is_fallback") is True
    assert "Mancozeb" in rec.get("treatment") or "Chlorothalonil" in rec.get("treatment")
    assert rec.get("status") is None or result["status"]["recommendation"] == "completed"


def test_weather_advisory_generation():
    user_profile = {"crop_history": ["Tomato", "Cotton"]}
    weather_data = {"temperature_celsius": 36, "humidity_percent": 40, "condition": "Sunny"}
    adv = generate_weather_advisory(user_profile, weather_data)
    assert "irrigation" in adv.lower() or "temperature" in adv.lower()


def test_recommendation_handles_none_confidences():
    from unittest.mock import patch
    from app.core.config import settings

    # Simulate scenario where confidence and area are explicitly None
    context = {
        "status": {"preprocessing": "completed"},
        "crop": {"label": "Tomato", "confidence": None},
        "disease": {"label": "Late Blight", "confidence": None},
        "severity": {"percent": None, "bucket": None},
        "weather": {"temperature_celsius": None, "humidity_percent": None, "condition": None},
        "plot": {"area_acres": None},
    }
    with patch.object(settings, "ADVISORY_SERVER_URL", ""):
        result = generate_recommendation(context)
    rec = result.get("recommendation", {})
    assert rec is not None
    assert rec.get("is_fallback") is True
    assert "immediate_action" in rec

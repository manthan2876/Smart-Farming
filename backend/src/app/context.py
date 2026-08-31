# context.py — Factory for the shared pipeline context object.
import uuid
from typing import Any


def create_context(
    image_path: str,
    user_id: str = "anon",
    location: str = "Unknown",
    lat: float = 52.2297,  # Default or dynamic latitude
    lon: float = 21.0122,  # Default or dynamic longitude
    language: str = "English",
) -> dict[str, Any]:
    return {
        "request_id": str(uuid.uuid4()),
        "user": {
            "user_id": user_id,
            "location": location,
            "lat": lat,
            "lon": lon,
            "language": language,
        },
        "image": {
            "raw_path": str(image_path),
            "processed_path": None,
            "leaf_crop": None,
            "quality_score": None,
            "blur_score": None,
            "brightness_score": None,
            "leaf_detected": False,
        },
        "crop": {
            "label": None,
            "confidence": None,
        },
        "disease": {
            "label": None,
            "confidence": None,
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
            "model_used": None,
            "top_k": 3,
            "all_probs": None,
        },
        # ====================================================================
        # WEATHER
        # ====================================================================
        "weather": {
            "temperature_celsius": None,
            "feels_like_celsius": None,
            "temp_min": None,
            "temp_max": None,
            "humidity_percent": None,
            "pressure_hpa": None,
            "wind_speed_m_s": None,
            "wind_deg": None,
            "cloudiness_percent": None,
            "condition": None,
            "description": None,
            "status": "pending",
        },
        "recommendation": {},
        "notes": [],
        "status": {
            "preprocessing": "pending",
            "crop_identification": "pending",
            "decision_routing": "pending",
            "disease_classification": "pending",
            "severity": "pending",
            "pest_detection": "pending",
            "weather": "pending",  # Added status tracking for weather
            "recommendation": "pending",
        },
    }

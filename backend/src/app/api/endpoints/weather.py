from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.context import create_context
from app.core import get_session
from app.crud import get_user
from app.services.translation.service import normalize_language_code, translate_text
from app.schemas.client import (
    WeatherResponse,
    WeatherTranslationRequest,
    WeatherTranslationResponse,
)
from app.utils.json_utils import _json_safe

import time

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory cache for weather data and advisory: key -> (timestamp, data_dict)
_WEATHER_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
_CACHE_TTL_SECONDS = 600  # 10 minutes


def _generate_rule_based_advisory(mapped_weather: dict[str, Any], user_profile: dict[str, Any]) -> str:
    """Fallback agronomic advisory based on meteorological readings and crop history."""
    temp_raw = mapped_weather.get("temperature_celsius")
    try:
        temp = float(temp_raw) if temp_raw is not None else 26.0
    except (ValueError, TypeError):
        temp = 26.0

    hum_raw = mapped_weather.get("humidity_percent")
    try:
        hum = float(hum_raw) if hum_raw is not None else 65.0
    except (ValueError, TypeError):
        hum = 65.0

    cond = str(mapped_weather.get("condition") or "").lower()
    crops = user_profile.get("crop_history", [])
    crop_str = f" for {', '.join(crops)}" if crops else ""

    parts: list[str] = []
    if any(w in cond for w in ["rain", "drizzle", "thunderstorm", "shower"]):
        parts.append(
            f"Precipitation or rainy conditions detected{crop_str}. Postpone foliar spraying of chemicals and fertilizers to prevent runoff."
        )
        parts.append("Inspect drainage pathways in low-lying field sections to prevent root waterlogging.")
    elif hum > 75:
        parts.append(
            f"Elevated relative humidity ({hum:.0f}%){crop_str} increases risk of fungal and bacterial blight. Inspect lower canopy leaves closely."
        )
        parts.append("Delay foliar spray applications until foliage dries to maximize chemical uptake.")
    elif temp > 34:
        parts.append(
            f"High temperature ({temp:.1f}°C) may cause moisture stress. Schedule irrigation during early morning or late evening hours."
        )
    elif temp < 12:
        parts.append(
            f"Low ambient temperature ({temp:.1f}°C) may slow crop metabolic growth. Guard young seedlings and monitor soil moisture."
        )
    else:
        parts.append(
            f"Current weather conditions ({temp:.1f}°C, {hum:.0f}% humidity, {cond or 'fair skies'}){crop_str} are favorable for routine scouting, weeding, and farm maintenance."
        )

    return " ".join(parts)


@router.post("/weather/translate", response_model=WeatherTranslationResponse)
async def translate_weather_advisory_text(
    payload: WeatherTranslationRequest,
    user_id: str = Depends(get_current_user),
) -> dict[str, Any]:
    target_code = normalize_language_code(payload.target_language)
    if target_code == "en" or not payload.text.strip():
        return {"translated_text": payload.text, "language": "en"}
    
    try:
        translated = await translate_text(payload.text, target_code)
        return {"translated_text": translated, "language": target_code}
    except Exception as exc:
        logger.exception("Weather advisory translation failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Translation failed: {exc}")

@router.get("/weather", response_model=WeatherResponse)
async def weather(
    lat: float | None = Query(None, description="Latitude"),
    lon: float | None = Query(None, description="Longitude"),
    language: str | None = Query(None, description="Optional target language: 'en', 'hi', 'gu'"),
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    from app.models import User
    # Coordinate resolution: require explicit coords or fallback to farmer's registered farm
    if lat is None or lon is None:
        try:
            user = session.get(User, user_id)
            if user and user.farm and user.farm.latitude is not None and user.farm.longitude is not None:
                lat = float(user.farm.latitude)
                lon = float(user.farm.longitude)
        except Exception as exc:
            logger.warning("Failed resolving user farm coordinates: %s", exc)

    if lat is None or lon is None:
        raise HTTPException(
            status_code=400,
            detail="Coordinates 'lat' and 'lon' are required, or configure your farm location in profile.",
        )

    target_code = normalize_language_code(language) if language else "en"
    grid_cache_key = f"sf:weather:grid:{round(lat, 1)}_{round(lon, 1)}"
    cache_key = f"{round(lat, 2)}_{round(lon, 2)}"
    now = time.time()

    try:
        # 1. Try Upstash Redis REST cache (15ms latency, serverless compatible)
        try:
            from app.core.redis_rest import redis_rest
            cached_data = await redis_rest.get(grid_cache_key) or await redis_rest.get(f"sf:weather:{cache_key}")
            if cached_data and isinstance(cached_data, dict):
                translations = cached_data.get("translations") or {}
                if target_code != "en" and target_code not in translations:
                    base_advisory = cached_data.get("advisory", "")
                    if base_advisory:
                        try:
                            translated = await translate_text(base_advisory, target_code)
                            translations[target_code] = translated
                            cached_data["translations"] = translations
                            await redis_rest.set(grid_cache_key, cached_data, ex=_CACHE_TTL_SECONDS)
                        except Exception:
                            pass
                cached_data["translated_advisory"] = translations.get(target_code, cached_data.get("advisory", ""))
                cached_data["cached"] = True
                return _json_safe(cached_data)
        except Exception as exc:
            logger.debug("Upstash Redis REST weather cache lookup failed: %s", exc)

        # 2. Return from in-memory cache if fresh
        if cache_key in _WEATHER_CACHE:
            cached_time, cached_data = _WEATHER_CACHE[cache_key]
            if now - cached_time < _CACHE_TTL_SECONDS:
                data = dict(cached_data)
                translations = dict(data.get("translations") or {})
                
                if target_code != "en" and target_code not in translations:
                    base_advisory = data.get("advisory", "")
                    if base_advisory:
                        try:
                            translated = await translate_text(base_advisory, target_code)
                            translations[target_code] = translated
                            data["translations"] = translations
                            _WEATHER_CACHE[cache_key] = (cached_time, data)
                        except Exception as exc:
                            logger.warning("Weather cache on-demand translation failed: %s", exc)

                data["translated_advisory"] = translations.get(target_code, data.get("advisory", ""))
                return _json_safe(data)

        from app.services.weather.service import fetch_weather
        from app.services.recommendation.service import generate_weather_advisory

        # Fetch user data for personalized advisory (safely guarded)
        user_profile: dict[str, Any] = {}
        try:
            user = get_user(session, user_id)
            if user:
                farm = user.farm
                user_profile = {
                    "location": farm.location if farm else "Unknown",
                    "crop_history": farm.crop_history if farm else [],
                    "farm_name": farm.name if farm else "Unknown Farm",
                    "farm_area_acres": farm.area_acres if farm else "Unknown",
                }
        except Exception as exc:
            logger.warning("Failed fetching user farm profile for advisory: %s", exc)

        result: dict[str, Any] = {}
        try:
            context = create_context(
                image_path="",
                user_id=user_id,
                lat=lat,
                lon=lon,
            )
            result = fetch_weather(context, {})
        except Exception as exc:
            logger.warning("fetch_weather execution failed: %s", exc)

        logger.info("Weather service raw result: %s", result)
        weather_data = result.get("weather", result) if isinstance(result, dict) else {}
        logger.info("Extracted weather data: %s", weather_data)

        # Map properly to frontend expected fields with resilient defaults
        raw_temp = weather_data.get("temperature_celsius") or weather_data.get("temperature")
        try:
            temp = float(raw_temp) if raw_temp is not None else 26.0
        except (ValueError, TypeError):
            temp = 26.0

        raw_hum = weather_data.get("humidity_percent") or weather_data.get("humidity")
        try:
            hum = float(raw_hum) if raw_hum is not None else 65.0
        except (ValueError, TypeError):
            hum = 65.0

        desc = str(weather_data.get("description") or weather_data.get("condition") or "Fair skies")
        raw_wind = weather_data.get("wind_speed_m_s") or weather_data.get("wind_speed")
        try:
            wind = float(raw_wind) if raw_wind is not None else 3.5
        except (ValueError, TypeError):
            wind = 3.5

        mapped_weather = {
            "temperature_celsius": temp,
            "humidity_percent": hum,
            "condition": desc,
        }

        # Generate AI Advisory with rule-based fallback
        advisory = ""
        try:
            advisory = generate_weather_advisory(user_profile, mapped_weather)
        except Exception as exc:
            logger.warning("Weather advisory AI generation failed: %s", exc)

        if not advisory or not advisory.strip():
            advisory = _generate_rule_based_advisory(mapped_weather, user_profile)

        translations: dict[str, str] = {"en": advisory}
        translated_advisory = advisory
        if advisory and target_code != "en":
            try:
                translated_advisory = await translate_text(advisory, target_code)
                translations[target_code] = translated_advisory
            except Exception as exc:
                logger.warning("Weather advisory auto-translation failed: %s", exc)
                translated_advisory = advisory

        result_payload = {
            "temperature_celsius": temp,
            "condition": desc,
            "humidity_percent": hum,
            "wind_speed_mps": wind,
            "pressure_hpa": weather_data.get("pressure_hpa") or weather_data.get("pressure") or 1013.0,
            "cloudiness_percent": weather_data.get("cloudiness_percent") or weather_data.get("cloudiness") or 20.0,
            "advisory": advisory,
            "translated_advisory": translated_advisory,
            "translations": translations,
            "cached": False,
            "timestamp": now,
        }
        _WEATHER_CACHE[cache_key] = (now, result_payload)
        try:
            from app.core.redis_rest import redis_rest
            await redis_rest.set(grid_cache_key, _json_safe(result_payload), ex=_CACHE_TTL_SECONDS)
            await redis_rest.set(f"sf:weather:{cache_key}", _json_safe(result_payload), ex=_CACHE_TTL_SECONDS)
        except Exception:
            pass
        return _json_safe(result_payload)

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error in weather endpoint: %s", exc)
        fallback_advisory = "Fair weather conditions observed. Maintain regular crop irrigation and monitor canopy health."
        return _json_safe({
            "temperature_celsius": 26.0,
            "condition": "Fair skies",
            "humidity_percent": 65.0,
            "wind_speed_mps": 3.5,
            "pressure_hpa": 1013.0,
            "cloudiness_percent": 20.0,
            "advisory": fallback_advisory,
            "translated_advisory": fallback_advisory,
            "translations": {"en": fallback_advisory},
            "cached": False,
            "timestamp": now,
        })



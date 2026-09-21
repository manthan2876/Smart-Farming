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
from app.utils.json_utils import _json_safe

logger = logging.getLogger(__name__)

router = APIRouter()

class WeatherTranslationRequest(BaseModel):
    text: str
    target_language: str

@router.post("/weather/translate")
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

@router.get("/weather")
async def weather(
    lat: float = 52.2297,
    lon: float = 21.0122,
    language: str | None = Query(None, description="Optional target language: 'en', 'hi', 'gu'"),
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    from app.services.weather.service import fetch_weather
    from app.services.recommendation.service import generate_weather_advisory

    # Fetch user data for personalized advisory
    user = get_user(session, user_id)
    user_profile = {}
    if user:
        farm = user.farm
        user_profile = {
            "location": farm.location if farm else "Unknown",
            "crop_history": farm.crop_history if farm else [],
            "farm_name": farm.name if farm else "Unknown Farm",
            "farm_area_acres": farm.area_acres if farm else "Unknown",
        }

    context = create_context(
        image_path="",
        user_id=user_id,
        lat=lat,
        lon=lon,
    )
    result = fetch_weather(context, {})
    
    logger.info(f"Weather service raw result: {result}")
    
    weather_data = result.get("weather", result) if isinstance(result, dict) else {}
    
    logger.info(f"Extracted weather data: {weather_data}")
    
    # Map properly to frontend expected fields
    temp = weather_data.get("temperature_celsius") or weather_data.get("temperature")
    hum = weather_data.get("humidity_percent") or weather_data.get("humidity")
    desc = weather_data.get("description", "Clear skies")
    wind = weather_data.get("wind_speed_m_s") or weather_data.get("wind_speed")
    
    # Generate AI Advisory
    mapped_weather = {
        "temperature_celsius": temp,
        "humidity_percent": hum,
        "condition": desc,
    }
    advisory = generate_weather_advisory(user_profile, mapped_weather)

    target_code = normalize_language_code(language) if language else "en"
    translated_advisory = ""
    translations: dict[str, str] = {}
    if advisory and target_code != "en":
        try:
            translated_advisory = await translate_text(advisory, target_code)
            translations[target_code] = translated_advisory
        except Exception as exc:
            logger.warning("Weather advisory auto-translation failed: %s", exc)
            translated_advisory = advisory

    return _json_safe({
        "temperature_celsius": temp,
        "condition": desc,
        "humidity_percent": hum,
        "wind_speed_mps": wind,
        "pressure_hpa": weather_data.get("pressure_hpa") or weather_data.get("pressure"),
        "cloudiness_percent": weather_data.get("cloudiness_percent") or weather_data.get("cloudiness"),
        "advisory": advisory,
        "translated_advisory": translated_advisory if target_code != "en" else advisory,
        "translations": translations,
    })

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.context import create_context
from app.core import get_session
from app.crud import get_user
from app.utils.json_utils import _json_safe

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/weather")
async def weather(
    lat: float = 52.2297,
    lon: float = 21.0122,
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

    return _json_safe({
        "temperature_celsius": temp,
        "condition": desc,
        "humidity_percent": hum,
        "wind_speed_mps": wind,
        "pressure_hpa": weather_data.get("pressure_hpa") or weather_data.get("pressure"),
        "cloudiness_percent": weather_data.get("cloudiness_percent") or weather_data.get("cloudiness"),
        "advisory": advisory,
    })

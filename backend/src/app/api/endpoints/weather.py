from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends

from app.api import get_current_user
from app.context import create_context

router = APIRouter()

def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {
            str(key): _json_safe(item)
            for key, item in value.items()
            if not str(key).startswith("_")
        }
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "tolist"):
        return _json_safe(value.tolist())
    return str(value)

@router.get("/weather")
async def weather(
    lat: float = 52.2297,
    lon: float = 21.0122,
    user_id: str = Depends(get_current_user),
) -> dict[str, Any]:
    from app.services.weather.service import fetch_weather

    context = create_context(
        image_path="",
        user_id=user_id,
        lat=lat,
        lon=lon,
    )
    result = fetch_weather(context, {})
    return _json_safe(result.get("weather", {}))
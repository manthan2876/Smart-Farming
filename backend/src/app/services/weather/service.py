import os
import requests
from dotenv import load_dotenv

load_dotenv()


def fetch_weather(context: dict, config: dict | None = None) -> dict:
    """
    Fetches current weather data from OpenWeather using coordinates
    from context['user'] and populates context['weather'].
    """

    if config is None:
        config = {}
    
    user_info = context.get("user", {})
    lat = user_info.get("lat")
    lon = user_info.get("lon")
    api_key = os.environ.get("OPENWEATHER_API")

    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).isoformat()

    if lat is None or lon is None:
        context["weather"] = {
            "provider": "OpenWeatherMap",
            "timestamp": now_iso,
            "is_degraded": True,
            "status": "missing_coordinates",
            "message": "Coordinates not provided for weather lookup.",
        }
        context["status"]["weather"] = "skipped"
        return context

    # 1. Coordinate grid caching (0.1° cell ~11km) to conserve OpenWeatherMap API quota
    try:
        from app.core.redis_rest import redis_rest
        grid_lat = round(float(lat), 1)
        grid_lon = round(float(lon), 1)
        grid_cache_key = f"sf:weather:grid:{grid_lat}_{grid_lon}"
        cached_weather = redis_rest.get_sync(grid_cache_key)
        if cached_weather and isinstance(cached_weather, dict) and cached_weather.get("status") == "success":
            cached_weather["timestamp"] = now_iso
            context["weather"] = cached_weather
            context["status"]["weather"] = "completed"
            return context
    except Exception:
        pass

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        if response.status_code == 200:
            weather_payload = {
                "provider": "OpenWeatherMap",
                "timestamp": now_iso,
                "is_degraded": False,
                "temperature_celsius": data["main"]["temp"],
                "feels_like_celsius": data["main"]["feels_like"],
                "temp_min": data["main"]["temp_min"],
                "temp_max": data["main"]["temp_max"],
                "humidity_percent": data["main"]["humidity"],
                "pressure_hpa": data["main"]["pressure"],
                "wind_speed_m_s": data["wind"]["speed"],
                "wind_deg": data["wind"]["deg"],
                "cloudiness_percent": data["clouds"]["all"],
                "condition": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "status": "success",
            }
            context["weather"] = weather_payload
            context["status"]["weather"] = "completed"

            # Cache the successful microclimate reading for 30 minutes (1800s)
            try:
                from app.core.redis_rest import redis_rest
                redis_rest.set_sync(grid_cache_key, weather_payload, ex=1800)
            except Exception:
                pass
        else:
            context["weather"] = {
                "provider": "OpenWeatherMap",
                "timestamp": now_iso,
                "is_degraded": True,
                "status": "failed",
                "message": data.get("message", "Unknown error"),
            }
            context["status"]["weather"] = "failed"

    except Exception as exc:
        context["weather"] = {
            "provider": "OpenWeatherMap",
            "timestamp": now_iso,
            "is_degraded": True,
            "status": "error",
            "message": str(exc),
        }
        context["status"]["weather"] = "failed"
        context["notes"].append(f"Weather fetch error: {exc}")

    return context

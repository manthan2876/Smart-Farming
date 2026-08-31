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
    lat = user_info.get("lat", 52.2297)
    lon = user_info.get("lon", 21.0122)
    api_key = os.environ.get("OPENWEATHER_API")

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            context["weather"] = {
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
            context["status"]["weather"] = "completed"
        else:
            context["weather"] = {
                "status": "failed",
                "message": data.get("message", "Unknown error"),
            }
            context["status"]["weather"] = "failed"

    except Exception as exc:
        context["weather"] = {"status": "error", "message": str(exc)}
        context["status"]["weather"] = "failed"
        context["notes"].append(f"Weather fetch error: {exc}")

    return context

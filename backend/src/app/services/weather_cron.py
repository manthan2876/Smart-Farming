import os
import httpx
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from app.core import get_session
from app.core.database import SessionLocal
from app.models.farm import Farm
from app.models.alert import Alert

logger = logging.getLogger("smart-farming.weather")

OPENWEATHER_API = os.getenv("OPENWEATHER_API")

async def check_weather_risk():
    if not OPENWEATHER_API:
        logger.warning("OPENWEATHER_API not set, skipping weather cron.")
        return

    logger.info("Running weather risk evaluation...")
    db = SessionLocal()
    try:
        farms = db.query(Farm).all()
        async with httpx.AsyncClient() as client:
            for farm in farms:
                if not farm.latitude or not farm.longitude:
                    continue
                
                url = f"https://api.openweathermap.org/data/2.5/weather?lat={farm.latitude}&lon={farm.longitude}&appid={OPENWEATHER_API}&units=metric"
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    temp = data.get("main", {}).get("temp", 0)
                    humidity = data.get("main", {}).get("humidity", 0)
                    
                    # Risk Rule: High humidity and warm temp = Early Blight risk
                    if humidity > 75 and 20 <= temp <= 28:
                        # Check if alert already exists recently
                        existing = db.query(Alert).filter(
                            Alert.user_id == farm.user_id,
                            Alert.kind == "weather_risk"
                        ).first()
                        if not existing:
                            alert = Alert(
                                user_id=farm.user_id,
                                kind="weather_risk",
                                title="High Disease Risk (Early Blight)",
                                body=f"Local conditions (Humidity {humidity}%, Temp {temp}°C) indicate a high risk for Early Blight. Consider preventative fungicides."
                            )
                            db.add(alert)
        db.commit()
    except Exception as e:
        logger.error(f"Weather cron error: {e}")
        db.rollback()
    finally:
        db.close()

def start_weather_cron():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_weather_risk, "interval", hours=4)
    scheduler.start()

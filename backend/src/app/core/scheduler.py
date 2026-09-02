import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.core.session import _session_factory
from app.models import Farm, Alert, Plot
from app.services.weather.service import fetch_weather
from app.context import create_context

logger = logging.getLogger("smart-farming.scheduler")
scheduler = AsyncIOScheduler()

async def evaluate_weather_risks():
    logger.info("Evaluating weather risks for all active plots...")
    db: Session = _session_factory()()
    try:
        plots = db.query(Plot).join(Farm).filter(Farm.latitude.isnot(None), Farm.longitude.isnot(None)).all()
        for plot in plots:
            farm = plot.farm
            try:

                context = create_context(image_path="", user_id=farm.user_id, lat=farm.latitude, lon=farm.longitude)
                result = fetch_weather(context, {})
                weather_data = result.get("weather", {})
                temp = weather_data.get("temperature_celsius") or weather_data.get("temperature", 0)
                humidity = weather_data.get("humidity_percent") or weather_data.get("humidity", 0)

                
                # Simple epidemiological threshold logic (e.g. for Tomatoes)
                if humidity > 75 and 20 <= temp <= 28 and (plot.crop or "").lower() == "tomato":
                    # Check if an alert already exists in the last 24 hours
                    existing = db.query(Alert).filter(
                        Alert.plot_id == plot.id,
                        Alert.kind == "weather_risk"
                    ).order_by(Alert.created_at.desc()).first()
                    
                    if not existing or existing.is_read:
                        alert = Alert(
                            user_id=farm.user_id,
                            plot_id=plot.id,
                            kind="weather_risk",
                            severity="high",
                            title=f"High Blight Risk: {plot.name}",
                            body=f"Humidity ({humidity}%) and Temperature ({temp}°C) create optimal conditions for Early Blight. Consider preventative fungicides.",
                            is_read=False
                        )
                        db.add(alert)
            except Exception as e:
                logger.error(f"Failed to check weather for plot {plot.id}: {e}")
        db.commit()
        logger.info("Weather risk evaluation completed.")
    except Exception as e:
        logger.error(f"Weather evaluation job failed: {e}")
    finally:
        db.close()

def start_scheduler():
    scheduler.add_job(
        evaluate_weather_risks,
        CronTrigger(hour="*/6"), # Run every 6 hours
        id="weather_risk_eval",
        replace_existing=True
    )
    scheduler.start()
    logger.info("APScheduler started successfully.")

def shutdown_scheduler():
    scheduler.shutdown()
    logger.info("APScheduler stopped.")

from arq.connections import RedisSettings

from arq.cron import cron
from urllib.parse import urlparse
from app.services.weather.proactive import evaluate_weather_risks
from app.core.session import _session_factory
from pathlib import Path
from app.models.image import Image
from app.core.config import settings
from app.core.paths import ensure_storage_directories, storage_relative_path

ensure_storage_directories()

async def purge_orphaned_blobs_cron(ctx):
    logger.info("Running scheduled orphaned blob cleanup...")
    
    # We do this in a background thread or just synchronously since it's a cron
    db = _session_factory()()
    try:
        db_images = db.query(Image).all()
        valid_paths = set()
        for img in db_images:
            if img.raw_path:
                valid_paths.add(img.raw_path.replace("\\", "/"))
            if img.processed_path:
                valid_paths.add(img.processed_path.replace("\\", "/"))
                
        deleted_count = 0
        directories_to_clean = [settings.UPLOAD_ROOT, settings.PROCESSED_ROOT, settings.AUDIO_ROOT]
        
        for dir_path in directories_to_clean:
            folder = Path(dir_path)
            if folder.exists():
                for file in folder.glob("*"):
                    if file.is_file():
                        rel_path = storage_relative_path(file)
                        if rel_path not in valid_paths:
                            file.unlink()
                            deleted_count += 1
        logger.info(f"Scheduled cleanup finished. Deleted {deleted_count} orphaned files.")
    except Exception as e:
        logger.error(f"Error during orphaned blob cleanup: {e}")
    finally:
        db.close()

import logging
from app.services.prediction_job import run_prediction_job
import asyncio

logger = logging.getLogger("smart-farming.arq")

async def process_prediction_job(
    ctx,
    prediction_id: int,
    user_id: str,
    relative_image_path: str,
    location: str,
    lat: float,
    lon: float,
    language: str,
    is_rescan: bool = False,
    parent_id: int | None = None,
    plot_id: int | None = None,
):
    logger.info(f"Starting ARQ job for prediction {prediction_id}")
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, 
        run_prediction_job,
        prediction_id, 
        user_id, 
        relative_image_path, 
        location,
        lat,
        lon,
        language,
        is_rescan, 
        parent_id,
        plot_id,
    )
    logger.info(f"Completed ARQ job for prediction {prediction_id}")

class WorkerSettings:
    functions = [process_prediction_job]
    cron_jobs = [
        cron(purge_orphaned_blobs_cron, hour=3, minute=0, day=6),  # Run at 3:00 AM every Sunday
        cron(evaluate_weather_risks, hour={6, 12, 18}, minute=0),  # Run 3x/day for proactive alerts
    ]
    max_jobs = 2
    job_timeout = 900
    max_tries = 3
    redis_settings = RedisSettings(
        host=urlparse(settings.REDIS_URL).hostname or "127.0.0.1",
        port=urlparse(settings.REDIS_URL).port or 6379,
    )

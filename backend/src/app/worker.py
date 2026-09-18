from arq.connections import RedisSettings

from arq.cron import cron
from app.services.weather.proactive import evaluate_weather_risks
from app.core.session import _session_factory
from pathlib import Path
from app.models.image import Image

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
        directories_to_clean = ["data/uploads", "data/processed"]
        
        for dir_path in directories_to_clean:
            folder = Path(dir_path)
            if folder.exists():
                for file in folder.glob("*"):
                    if file.is_file():
                        rel_path = f"{dir_path}/{file.name}"
                        if rel_path not in valid_paths:
                            file.unlink()
                            deleted_count += 1
        logger.info(f"Scheduled cleanup finished. Deleted {deleted_count} orphaned files.")
    except Exception as e:
        logger.error(f"Error during orphaned blob cleanup: {e}")
    finally:
        db.close()

import logging
from app.api.endpoints.predict import run_background_pipeline
import asyncio

logger = logging.getLogger("smart-farming.arq")

async def process_prediction_job(ctx, prediction_id: int, user_id: str, context: dict, relative_image_path: str, is_rescan: bool = False, parent_id: int = None):
    # run_background_pipeline is a synchronous function that blocks the thread.
    # To run it properly without blocking the ARQ event loop, we run it in a threadpool.
    logger.info(f"Starting ARQ job for prediction {prediction_id}")
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, 
        run_background_pipeline, 
        prediction_id, 
        user_id, 
        context, 
        relative_image_path, 
        is_rescan, 
        parent_id
    )
    logger.info(f"Completed ARQ job for prediction {prediction_id}")

class WorkerSettings:
    functions = [process_prediction_job]
    cron_jobs = [
        cron(purge_orphaned_blobs_cron, hour=3, minute=0, day=6),  # Run at 3:00 AM every Sunday
        cron(evaluate_weather_risks, hour={6, 12, 18}, minute=0),  # Run 3x/day for proactive alerts
    ]
    redis_settings = RedisSettings(host="127.0.0.1", port=6379)

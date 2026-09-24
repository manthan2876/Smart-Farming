import asyncio
import logging
import time
from pathlib import Path
from urllib.parse import urlparse

from arq.connections import RedisSettings
from arq.cron import cron

from app.core.config import settings
from app.core.paths import ensure_storage_directories, storage_relative_path
from app.core.session import _session_factory
from app.models.image import Image
from app.services.prediction_job import run_prediction_job
from app.services.weather.proactive import evaluate_weather_risks

logger = logging.getLogger("smart-farming.arq")

ensure_storage_directories()

# Files newer than this are never purged: an in-flight prediction may have written its
# upload / processed image before the matching DB row is committed.
_ORPHAN_GRACE_SECONDS = 60 * 60


def _purge_orphaned_blobs() -> int:
    """Blocking implementation, run in a worker thread by the cron wrapper below."""
    from app.core.storage import purge_orphaned_blobs
    db = _session_factory()()
    try:
        res = purge_orphaned_blobs(db, dry_run=False, grace_seconds=_ORPHAN_GRACE_SECONDS)
        return res.get("deleted_files", 0)
    finally:
        db.close()


async def purge_orphaned_blobs_cron(ctx):
    logger.info("Running scheduled orphaned blob cleanup...")
    try:
        # Off the event loop: this does a full-table scan plus filesystem work.
        deleted_count = await asyncio.to_thread(_purge_orphaned_blobs)
        logger.info(f"Scheduled cleanup finished. Deleted {deleted_count} orphaned files.")
    except Exception as e:
        logger.error(f"Error during orphaned blob cleanup: {e}", exc_info=True)


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
    try:
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
    except Exception:
        logger.exception(f"ARQ job for prediction {prediction_id} failed")
        raise
    logger.info(f"Completed ARQ job for prediction {prediction_id}")


async def translate_entity_job(
    ctx,
    entity_type: str,
    entity_id: str,
    fields: dict[str, str],
    name_fields: list[str] | None = None,
):
    """Background ARQ job that processes translations and transliterations via Redis."""
    from app.services.translation.manager import process_entity_translation_sync

    logger.info("Executing translation job via Redis for %s #%s (fields: %s)", entity_type, entity_id, list(fields.keys()))
    db = _session_factory()()
    try:
        stats = await asyncio.to_thread(
            process_entity_translation_sync,
            db,
            entity_type,
            str(entity_id),
            fields,
            name_fields or [],
        )
        logger.info("Finished translation job for %s #%s: %s", entity_type, entity_id, stats)
        return stats
    finally:
        db.close()


async def on_startup(ctx):
    # The arq CLI only configures the 'arq' logger. Without this, INFO/WARNING records from
    # 'smart-farming.*' (e.g. "Unable to publish status ...") can be silently lost.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger("smart-farming").setLevel(logging.INFO)
    logger.info("Prediction worker started")


class WorkerSettings:
    functions = [process_prediction_job, translate_entity_job]
    on_startup = on_startup
    cron_jobs = [
        # weekday=6 -> Sunday (arq: Monday=0 ... Sunday=6). `day=` would mean day-of-month.
        cron(purge_orphaned_blobs_cron, weekday=6, hour=3, minute=0),
        cron(evaluate_weather_risks, hour={6, 12, 18}, minute=0),  # Run 3x/day for proactive alerts
    ]
    max_jobs = 2
    job_timeout = 900
    max_tries = 3
    redis_settings = RedisSettings(
        host=urlparse(settings.REDIS_URL).hostname or "127.0.0.1",
        port=urlparse(settings.REDIS_URL).port or 6379,
    )
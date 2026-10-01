import asyncio
import logging
import time
from pathlib import Path
from urllib.parse import urlparse

from arq.connections import RedisSettings

from app.core.config import settings
from app.core.paths import ensure_storage_directories, storage_relative_path
from app.core.session import _session_factory
from app.models.image import Image
from app.services.prediction_job import run_prediction_job

logger = logging.getLogger("smart-farming.arq")

ensure_storage_directories()



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
    mode = "Local Docker Redis" if settings.REQUIRE_REDIS else "Upstash Cloud Redis"
    target = urlparse(settings.REDIS_URL).hostname or settings.REDIS_URL
    logger.info("Prediction worker started [%s: %s]", mode, target)


def _get_worker_redis_settings() -> RedisSettings:
    url = getattr(settings, "REDIS_URL", None) or "redis://127.0.0.1:6379"
    try:
        rs = RedisSettings.from_dsn(url)
    except Exception as exc:
        logger.warning("Could not parse REDIS_URL '%s' (%s); falling back to default.", url, exc)
        rs = RedisSettings(host="127.0.0.1", port=6379)

    # Harden cloud connection timeouts and retries (especially for Upstash TLS over public internet)
    rs.conn_timeout = 15
    rs.conn_retries = 10
    rs.conn_retry_delay = 2
    rs.retry_on_timeout = True
    try:
        from redis.asyncio.retry import Retry
        from redis.backoff import ExponentialBackoff
        rs.retry = Retry(ExponentialBackoff(cap=10, base=1), retries=5)
        rs.retry_on_error = [ConnectionError, TimeoutError, OSError]
    except Exception:
        pass
    return rs


class WorkerSettings:
    functions = [process_prediction_job, translate_entity_job]
    on_startup = on_startup
    max_jobs = 2
    job_timeout = 900
    max_tries = 3
    # When connected to Upstash Cloud Redis, poll every 3.0s to conserve command quota; 0.5s for local Docker
    poll_delay = getattr(settings, "ARQ_POLL_DELAY", None) or (3.0 if not settings.REQUIRE_REDIS else 0.5)
    redis_settings = _get_worker_redis_settings()


# Patch ARQ Worker._poll_iteration to survive transient Redis connection resets / timeouts
from arq.worker import Worker
from redis.exceptions import ConnectionError as RedisConnectionError, TimeoutError as RedisTimeoutError, RedisError

_original_poll_iteration = Worker._poll_iteration

async def _resilient_poll_iteration(self) -> None:
    try:
        await _original_poll_iteration(self)
    except (RedisConnectionError, RedisTimeoutError, RedisError, TimeoutError, OSError, ConnectionResetError) as exc:
        logger.warning(
            "Transient Redis error during polling loop (%s: %s). Reconnecting on next iteration...",
            exc.__class__.__name__,
            exc,
        )
        await asyncio.sleep(getattr(self, "poll_delay_s", 2.0))
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        logger.exception("Unexpected error in ARQ poll iteration: %s", exc)
        await asyncio.sleep(getattr(self, "poll_delay_s", 2.0))

Worker._poll_iteration = _resilient_poll_iteration
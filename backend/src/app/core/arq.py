import logging
from urllib.parse import urlparse

from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import settings

logger = logging.getLogger(__name__)

arq_pool = None

async def init_arq():
    global arq_pool
    if not getattr(settings, "REQUIRE_REDIS", False):
        logger.info("REQUIRE_REDIS is False; skipping ARQ Redis pool initialization.")
        arq_pool = None
        return None

    parsed = urlparse(settings.REDIS_URL)
    redis_settings = RedisSettings(
        host=parsed.hostname or "127.0.0.1",
        port=parsed.port or 6379,
        password=parsed.password,
        database=int(parsed.path.lstrip("/") or 0),
    )
    try:
        arq_pool = await create_pool(redis_settings)
    except Exception:
        arq_pool = None
        if settings.REQUIRE_REDIS:
            raise
        logger.warning("Redis is unavailable; continuing without the ARQ job pool.")
    return arq_pool

async def close_arq():
    global arq_pool
    if arq_pool:
        await arq_pool.close()


async def enqueue_translation(
    entity_type: str,
    entity_id: str | int,
    fields: dict[str, str],
    name_fields: list[str] | None = None,
):
    """Enqueue translation job to the Redis ARQ queue."""
    global arq_pool
    if arq_pool is None:
        arq_pool = await init_arq()

    if arq_pool:
        try:
            job = await arq_pool.enqueue_job(
                "translate_entity_job",
                entity_type=entity_type,
                entity_id=str(entity_id),
                fields=fields,
                name_fields=name_fields or [],
            )
            logger.info("Enqueued translation job %s for %s #%s to Redis", getattr(job, "job_id", ""), entity_type, entity_id)
            return job
        except Exception as exc:
            logger.error("Failed to enqueue translation job to Redis: %s", exc)
            raise
    else:
        logger.error("Cannot enqueue translation job: ARQ Redis pool is not connected.")


def enqueue_translation_sync(
    entity_type: str,
    entity_id: str | int,
    fields: dict[str, str],
    name_fields: list[str] | None = None,
):
    """Synchronous helper for worker threads / non-async code to enqueue translation to Redis."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(enqueue_translation(entity_type, entity_id, fields, name_fields))
        else:
            loop.run_until_complete(enqueue_translation(entity_type, entity_id, fields, name_fields))
    except Exception:
        asyncio.run(enqueue_translation(entity_type, entity_id, fields, name_fields))


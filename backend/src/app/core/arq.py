import logging
from urllib.parse import urlparse

from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import settings

logger = logging.getLogger(__name__)

arq_pool = None

async def init_arq():
    global arq_pool
    try:
        redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
        arq_pool = await create_pool(redis_settings)
        mode = "Local Docker Redis" if settings.REQUIRE_REDIS else "Upstash Cloud Redis"
        logger.info("Initialized ARQ pool [%s: %s]", mode, redis_settings.host)
    except Exception as exc:
        arq_pool = None
        if getattr(settings, "REQUIRE_REDIS", False):
            logger.error("Failed to connect to required local Redis (%s): %s", settings.REDIS_URL, exc)
            raise
        logger.warning("Redis is unavailable (%s); continuing without the ARQ job pool.", exc)
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
        # Serverless / In-process execution (Cloud Run without 24/7 worker)
        # Runs in thread pool with Upstash Redis REST caching without blocking the event loop
        import asyncio
        from app.core.session import _session_factory
        from app.services.translation.manager import process_entity_translation_sync

        def _run_sync():
            db = _session_factory()()
            try:
                return process_entity_translation_sync(
                    session=db,
                    entity_type=entity_type,
                    entity_id=str(entity_id),
                    fields=fields,
                    name_fields=name_fields or [],
                )
            except Exception as e:
                logger.warning("In-process translation fallback error for %s #%s: %s", entity_type, entity_id, e)
            finally:
                db.close()

        logger.info("Executing translation in background thread (serverless mode) for %s #%s", entity_type, entity_id)
        return await asyncio.to_thread(_run_sync)


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


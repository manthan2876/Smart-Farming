import logging
from urllib.parse import urlparse

from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import settings

import asyncio
logger = logging.getLogger(__name__)

arq_pool = None
main_loop = None

async def init_arq():
    global arq_pool, main_loop
    try:
        main_loop = asyncio.get_running_loop()
    except RuntimeError:
        pass

    try:
        redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
        # Harden cloud connection timeouts and retries (especially for Upstash TLS over public internet)
        redis_settings.conn_timeout = 15
        redis_settings.conn_retries = 10
        redis_settings.conn_retry_delay = 2
        redis_settings.retry_on_timeout = True
        try:
            from redis.asyncio.retry import Retry
            from redis.backoff import ExponentialBackoff
            redis_settings.retry = Retry(ExponentialBackoff(cap=10, base=1), retries=5)
            redis_settings.retry_on_error = [ConnectionError, TimeoutError, OSError]
        except Exception:
            pass
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
    global arq_pool, main_loop
    if arq_pool:
        await arq_pool.close()
    main_loop = None


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
    """Synchronous helper for worker threads / non-async code to enqueue translation safely."""
    global main_loop
    coro = enqueue_translation(entity_type, entity_id, fields, name_fields)

    # 1. If the main FastAPI event loop is running, dispatch to it safely across threads
    if main_loop and main_loop.is_running():
        try:
            current_loop = None
            try:
                current_loop = asyncio.get_running_loop()
            except RuntimeError:
                pass

            if current_loop is main_loop:
                main_loop.create_task(coro)
            else:
                asyncio.run_coroutine_threadsafe(coro, main_loop)
            return
        except Exception as exc:
            logger.warning("Failed to dispatch translation to main event loop: %s", exc)

    # 2. Fallback for standalone worker threads: run in-process sync directly to avoid attaching arq_pool to a temporary loop
    try:
        from app.core.session import _session_factory
        from app.services.translation.manager import process_entity_translation_sync
        db = _session_factory()()
        try:
            process_entity_translation_sync(
                session=db,
                entity_type=entity_type,
                entity_id=str(entity_id),
                fields=fields,
                name_fields=name_fields or [],
            )
        except Exception as e:
            logger.warning("In-process translation sync error for %s #%s: %s", entity_type, entity_id, e)
        finally:
            db.close()
    except Exception as exc:
        logger.warning("Could not execute fallback translation: %s", exc)


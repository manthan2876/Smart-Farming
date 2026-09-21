import logging
from urllib.parse import urlparse

from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import settings

logger = logging.getLogger(__name__)

arq_pool = None

async def init_arq():
    global arq_pool
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

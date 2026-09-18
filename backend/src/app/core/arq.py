import logging
import os
from urllib.parse import urlparse

from arq import create_pool
from arq.connections import RedisSettings

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REQUIRE_REDIS = os.getenv("REQUIRE_REDIS", "false").lower() in {"1", "true", "yes"}

arq_pool = None

async def init_arq():
    global arq_pool
    parsed = urlparse(REDIS_URL)
    settings = RedisSettings(
        host=parsed.hostname or "127.0.0.1",
        port=parsed.port or 6379,
        password=parsed.password,
        database=int(parsed.path.lstrip("/") or 0),
    )
    try:
        arq_pool = await create_pool(settings)
    except Exception:
        arq_pool = None
        if REQUIRE_REDIS:
            raise
        logger.warning("Redis is unavailable; continuing without the ARQ job pool.")
    return arq_pool

async def close_arq():
    global arq_pool
    if arq_pool:
        await arq_pool.close()

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
# Parse redis url properly or just hardcode host for ARQ since it takes host/port
# arq RedisSettings defaults to localhost:6379 which matches our docker setup

arq_pool = None

async def init_arq():
    global arq_pool
    arq_pool = await create_pool(RedisSettings(host="localhost", port=6379))
    return arq_pool

async def close_arq():
    global arq_pool
    if arq_pool:
        await arq_pool.close()

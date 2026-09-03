from arq.connections import RedisSettings
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
    redis_settings = RedisSettings(host="localhost", port=6379)

import os
from pathlib import Path
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.endpoints.alerts import router as alerts_router
from app.api.endpoints.tts import router as tts_router
from app.api.endpoints.mlops import router as mlops_router
from app.api import (
    auth_router,
    profile_router,
    farm_router,
    predict_router,
    history_router,
    feedback_router,
    weather_router,
    crops_router,
    health_router,
    admin_router,
    expert_router,
)
from app.utils import configure_logging

configure_logging()

from contextlib import asynccontextmanager
from app.core.scheduler import start_scheduler, shutdown_scheduler
from app.services.weather_cron import start_weather_cron
from app.core.arq import init_arq, close_arq

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    app.state.arq_pool = await init_arq()
    start_weather_cron()
    yield
    await close_arq()
    shutdown_scheduler()


app = FastAPI(
    title="Smart Farming API",
    version="0.1.0",
    description="HTTP delivery layer for the Smart Farming diagnostic pipeline.",
    lifespan=lifespan
)

from app.core.limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)



allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173,http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all modular routers
app.include_router(tts_router)
app.include_router(mlops_router)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(farm_router)
app.include_router(predict_router)
app.include_router(history_router)
app.include_router(feedback_router)
app.include_router(weather_router)
app.include_router(crops_router)
app.include_router(health_router)
app.include_router(alerts_router)
app.include_router(admin_router)
app.include_router(expert_router)

# Mount static storage directories for uploaded and processed images
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_DATA_DIR = _BACKEND_DIR / "data"

print(f"-> Serving static files from: {_DATA_DIR.resolve()}")
_DATA_DIR.mkdir(parents=True, exist_ok=True)
(_DATA_DIR / "uploads").mkdir(parents=True, exist_ok=True)
(_DATA_DIR / "processed").mkdir(parents=True, exist_ok=True)

app.mount("/data", StaticFiles(directory=str(_DATA_DIR.resolve())), name="data")

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Smart Farming API", "docs": "/docs"}

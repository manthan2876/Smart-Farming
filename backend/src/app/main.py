import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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

app = FastAPI(
    title="Smart Farming API",
    version="0.1.0",
    description="HTTP delivery layer for the Smart Farming diagnostic pipeline.",
)

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
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all modular routers
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(farm_router)
app.include_router(predict_router)
app.include_router(history_router)
app.include_router(feedback_router)
app.include_router(weather_router)
app.include_router(crops_router)
app.include_router(health_router)
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

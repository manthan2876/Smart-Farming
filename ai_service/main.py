"""
ai_service/main.py — Root FastAPI application for the Smart Farming AI Service.
Combines Vision, IndicTrans2, Advisory, and Neural Indic-TTS in a single high-performance microservice.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path

# Add current directory to sys.path so modules resolve cleanly
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from routers.vision import router as vision_router
from routers.translation import router as translation_router
from routers.advisory import router as advisory_router
from routers.tts import router as tts_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
)
logger = logging.getLogger("ai_service")

app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.VERSION,
    description="Unified AI microservice for crop vision, Indic translation, agronomic advisory, and neural speech.",
    docs_url=None,       # Disable Swagger UI (/docs)
    redoc_url=None,      # Disable ReDoc (/redoc)
    openapi_url=None,    # Disable OpenAPI schema export (/openapi.json)
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # Allow public health check endpoints without secret
    if request.url.path in ("/", "/health"):
        return await call_next(request)

    # If GATEWAY_SECRET is configured, enforce Bearer authentication
    secret = settings.GATEWAY_SECRET
    if secret:
        auth_header = request.headers.get("Authorization", "")
        if auth_header != f"Bearer {secret}":
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized", "message": "Invalid or missing Bearer token."},
            )

    return await call_next(request)


@app.get("/")
@app.get("/health")
def root_health():
    uptime_sec = round(time.time() - START_TIME, 1)
    return {
        "service": "smart-farming-ai",
        "status": "active",
        "version": settings.VERSION,
        "device": settings.DEVICE,
        "cpu_threads": settings.CPU_THREADS,
        "uptime_seconds": uptime_sec,
        "routes": {
            "vision": "/vision/predict",
            "translation": "/translation/translate",
            "advisory": "/advisory/advise",
            "tts": "/tts/synthesize",
        },
    }


# Include routers with standard service prefixes
app.include_router(vision_router, prefix="/vision", tags=["Vision"])
app.include_router(translation_router, prefix="/translation", tags=["Translation"])
app.include_router(advisory_router, prefix="/advisory", tags=["Advisory"])
app.include_router(tts_router, prefix="/tts", tags=["TTS"])

# Direct aliases for stripped-path gateways
app.add_api_route("/predict", vision_router.routes[1].endpoint, methods=["POST"], tags=["Vision (Direct)"])
app.add_api_route("/translate", translation_router.routes[1].endpoint, methods=["POST"], tags=["Translation (Direct)"])
app.add_api_route("/advise", advisory_router.routes[1].endpoint, methods=["POST"], tags=["Advisory (Direct)"])
app.add_api_route("/synthesize", tts_router.routes[1].endpoint, methods=["POST"], tags=["TTS (Direct)"])


if __name__ == "__main__":
    import uvicorn
    # Hugging Face Spaces exposes port 7860
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=settings.DEBUG)

import logging
import re
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

import sys
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_SRC_DIR = Path(__file__).resolve().parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

load_dotenv(_BACKEND_DIR / ".env")

from app.api.endpoints.alerts import router as alerts_router
from app.api.endpoints.tts import router as tts_router
from app.api.endpoints.mlops import router as mlops_router
from app.api.endpoints.model_registry import router as model_registry_router
from app.api.endpoints.translation import router as translation_router
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
    internal_cron_router,
)
from app.utils import configure_logging

configure_logging()

import asyncio
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.arq import init_arq, close_arq
from app.core.init_db import initialize_database

logger = logging.getLogger("smart-farming.api")


def _log_background_task_failure(task: asyncio.Task) -> None:
    if task.cancelled():
        return
    exc = task.exception()
    if exc is not None:
        logger.error(
            "Background startup task failed",
            exc_info=(type(exc), exc, exc.__traceback__),
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    import time
    app.state.startup_time = time.time()

    # Sentry error tracking initialization (Phase 5 observability)
    if getattr(settings, "SENTRY_DSN", None):
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.SENTRY_ENVIRONMENT,
                traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
                send_default_pii=False,
                integrations=[FastApiIntegration(), SqlalchemyIntegration()],
            )
            logger.info("Sentry error tracking initialized for environment %s", settings.SENTRY_ENVIRONMENT)
        except Exception as exc:
            logger.warning("Could not initialize Sentry: %s", exc)

    # In local development, ensure tables exist immediately.
    # In production, run schema verification in the background so the HTTP port binds instantly (<1s)
    # and Render/health checks never time out during cold starts.
    if getattr(settings, "ENVIRONMENT", "development") != "production":
        initialize_database()
    else:
        db_task = asyncio.create_task(
            asyncio.to_thread(initialize_database),
            name="initialize-database",
        )
        db_task.add_done_callback(_log_background_task_failure)

    # Initialize ARQ pool only if Redis worker queue is explicitly required
    if getattr(settings, "REQUIRE_REDIS", False):
        app.state.arq_pool = await init_arq()
    else:
        app.state.arq_pool = None

    from app.api.endpoints.tts import sync_existing_audio_to_storage

    audio_task = asyncio.create_task(
        asyncio.to_thread(sync_existing_audio_to_storage),
        name="sync-audio-storage",
    )
    audio_task.add_done_callback(_log_background_task_failure)

    yield

    try:
        from app.core.redis_rest import redis_rest
        await redis_rest.aclose()
    except Exception:
        logger.exception("Failed to close Redis REST client during shutdown")
    try:
        await close_arq()
    except Exception:
        logger.exception("Failed to close ARQ pool during shutdown")

production_mode = settings.ENVIRONMENT.strip().lower() in {"production", "staging"}
app = FastAPI(
    title="Smart Farming API",
    version="0.1.0",
    description="HTTP delivery layer for the Smart Farming diagnostic pipeline.",
    docs_url=None if production_mode else "/docs",
    redoc_url=None if production_mode else "/redoc",
    openapi_url=None if production_mode else "/openapi.json",
    lifespan=lifespan,
)

from app.core.limiter import limiter

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unavailable")
    logger.exception(
        "Unhandled request error (request_id=%s, path=%s)",
        request_id,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error.", "request_id": request_id},
    )


@app.middleware("http")
async def add_request_id_and_security_headers(request: Request, call_next):
    incoming_id = request.headers.get("X-Request-ID", "")
    request_id = incoming_id if re.fullmatch(r"[A-Za-z0-9._-]{1,64}", incoming_id) else uuid.uuid4().hex
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


allowed_origins = [
    origin.strip().rstrip("/")
    for origin in settings.CORS_ORIGINS.split(",")
    if origin.strip()
]
if production_mode and not allowed_origins:
    raise RuntimeError("CORS_ORIGINS must contain the production frontend origin.")

cors_headers = ["Authorization", "Content-Type", "Accept", "Accept-Language", "X-Request-ID"]
if not production_mode:
    cors_headers.append("X-User-ID")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=cors_headers,
    expose_headers=["X-Request-ID", "X-Total-Count", "X-Offset", "X-Limit"],
)

api_routers = (
    tts_router,
    mlops_router,
    model_registry_router,
    translation_router,
    auth_router,
    profile_router,
    farm_router,
    predict_router,
    history_router,
    feedback_router,
    weather_router,
    crops_router,
    health_router,
    alerts_router,
    admin_router,
    expert_router,
    internal_cron_router,
)

# Keep existing unversioned clients working while documenting the versioned contract.
for api_router in api_routers:
    app.include_router(api_router, include_in_schema=False)
    app.include_router(api_router, prefix="/api/v1")

# Mount static storage directories for uploaded and processed images
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_DATA_DIR = _BACKEND_DIR / "data"

logger.info("Serving local media from %s", _DATA_DIR.resolve())
_DATA_DIR.mkdir(parents=True, exist_ok=True)
(_DATA_DIR / "uploads").mkdir(parents=True, exist_ok=True)
(_DATA_DIR / "processed").mkdir(parents=True, exist_ok=True)

@app.get("/data/{file_path:path}", include_in_schema=False)
def serve_data_file(file_path: str, request: Request):
    """Serve static asset from local disk or stream from Supabase Object Storage."""
    if production_mode:
        raise HTTPException(status_code=404, detail="File not found.")

    clean_subpath = file_path.replace("\\", "/").strip("/")
    if clean_subpath.startswith("data/"):
        clean_subpath = clean_subpath[5:]
    local_file = (_DATA_DIR / clean_subpath).resolve()
    try:
        local_file.relative_to(_DATA_DIR.resolve())
        if local_file.is_file():
            return FileResponse(local_file)
    except ValueError:
        pass

    backend_type = (settings.STORAGE_BACKEND or "local").lower()
    if backend_type in ("supabase", "s3"):
        try:
            from app.core.storage import get_storage
            storage = get_storage()
            data = storage.get(clean_subpath)
            content_type = "image/jpeg"
            lower_path = clean_subpath.lower()
            if lower_path.endswith(".png"):
                content_type = "image/png"
            elif lower_path.endswith(".webp"):
                content_type = "image/webp"
            elif lower_path.endswith(".mp3"):
                content_type = "audio/mpeg"
            return Response(
                content=data,
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=86400",
                    "Access-Control-Allow-Origin": "*",
                },
            )
        except FileNotFoundError:
            return JSONResponse(status_code=404, content={"detail": "File not found"})
        except Exception:
            logger.exception("Failed to retrieve stored media (request_id=%s)", getattr(request.state, "request_id", "unavailable"))
            return JSONResponse(status_code=503, content={"detail": "Stored media is temporarily unavailable."})

    return JSONResponse(status_code=404, content={"detail": "File not found"})


@app.get("/", include_in_schema=False)
async def root():
    response = {"message": "Smart Farming API"}
    if not production_mode:
        response["docs"] = "/docs"
    return response

from __future__ import annotations

import time
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core import get_session
from app.core.config import settings
from app.models.prediction import Prediction
from app.schemas import HealthResponse, QueueHealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="smart-farming-backend")


@router.get("/ready", response_model=HealthResponse)
def readiness(request: Request, session: Session = Depends(get_session)) -> HealthResponse:
    try:
        if hasattr(session, "execute"):
            session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is not ready.") from exc

    if getattr(settings, "REQUIRE_REDIS", False):
        arq_pool = getattr(request.app.state, "arq_pool", None)
        if arq_pool is None:
            raise HTTPException(status_code=503, detail="Worker queue is not ready.")

    return HealthResponse(status="ok", service="smart-farming-backend")


@router.get("/queue-health", response_model=QueueHealthResponse)
async def queue_health(request: Request) -> QueueHealthResponse:
    """Queue health inspection endpoint for worker status and queue saturation."""
    if not getattr(settings, "REQUIRE_REDIS", False):
        return QueueHealthResponse(
            status="ok",
            service="smart-farming-backend",
            mode="direct_sync",
            redis_connected=False,
            pending_jobs=0,
            worker_healthy=True,
            details={
                "execution_mode": "cloud_microservice",
                "caching": "upstash_rest_dedup",
                "message": "Direct pipeline execution active; standing ARQ worker pool is optional.",
            },
        )

    arq_pool = getattr(request.app.state, "arq_pool", None)
    if arq_pool is None:
        return QueueHealthResponse(
            status="degraded",
            service="smart-farming-backend",
            mode="arq_worker",
            redis_connected=False,
            pending_jobs=0,
            worker_healthy=False,
            details={"error": "ARQ pool is not connected or initialized."},
        )

    try:
        # Check Redis connectivity through the pool
        is_alive = await arq_pool.ping()
        pending = 0
        try:
            # Query ARQ default queue length if accessible
            pending = await arq_pool.zcard("arq:queue") or 0
        except Exception:
            # Fall back to 0 pending jobs if queue cardinality check fails
            pass

        return QueueHealthResponse(
            status="ok" if is_alive else "degraded",
            service="smart-farming-backend",
            mode="arq_worker",
            redis_connected=bool(is_alive),
            pending_jobs=int(pending),
            worker_healthy=bool(is_alive),
            details={"queue_name": "arq:queue", "max_jobs": 2, "job_timeout_seconds": 900},
        )
    except Exception as exc:
        return QueueHealthResponse(
            status="degraded",
            service="smart-farming-backend",
            mode="arq_worker",
            redis_connected=False,
            pending_jobs=0,
            worker_healthy=False,
            details={"error": str(exc)},
        )


@router.get("/metrics")
def metrics(request: Request, session: Session = Depends(get_session)) -> Response:
    """Expose Prometheus-formatted operational and business metrics (Phase 5 observability)."""
    startup_time = getattr(request.app.state, "startup_time", None) or time.time()
    uptime_seconds = round(time.time() - startup_time, 2)

    db_healthy = 1
    total_predictions = 0
    try:
        session.execute(text("SELECT 1"))
        total_predictions = session.scalar(select(func.count(Prediction.id))) or 0
    except Exception:
        db_healthy = 0

    mode_val = 1 if getattr(settings, "REQUIRE_REDIS", False) else 0
    has_arq = 1 if getattr(request.app.state, "arq_pool", None) is not None else 0

    lines = [
        "# HELP smart_farming_uptime_seconds Total seconds since application startup",
        "# TYPE smart_farming_uptime_seconds gauge",
        f"smart_farming_uptime_seconds {uptime_seconds}",
        "",
        "# HELP smart_farming_db_status Database connection status (1 = healthy, 0 = unhealthy)",
        "# TYPE smart_farming_db_status gauge",
        f"smart_farming_db_status {db_healthy}",
        "",
        "# HELP smart_farming_predictions_total Lifetime total of processed farmer predictions",
        "# TYPE smart_farming_predictions_total counter",
        f"smart_farming_predictions_total {total_predictions}",
        "",
        "# HELP smart_farming_worker_mode_enabled Whether ARQ worker mode is enforced via REQUIRE_REDIS (1 or 0)",
        "# TYPE smart_farming_worker_mode_enabled gauge",
        f"smart_farming_worker_mode_enabled {mode_val}",
        "",
        "# HELP smart_farming_worker_pool_active Whether the background ARQ pool is actively connected (1 or 0)",
        "# TYPE smart_farming_worker_pool_active gauge",
        f"smart_farming_worker_pool_active {has_arq}",
        "",
    ]
    return Response(content="\n".join(lines), media_type="text/plain; version=0.0.4; charset=utf-8")

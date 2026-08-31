from __future__ import annotations

import logging
from pathlib import Path
from fastapi import APIRouter
from app.schemas import HealthResponse

router = APIRouter()

_BACKEND_DIR = Path(__file__).resolve().parents[1]
_UPLOAD_DIR = _BACKEND_DIR / "data" / "uploads"
_MAX_UPLOAD_BYTES = 10 * 1024 * 1024
_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
_LOGGER = logging.getLogger("smart-farming.api")

@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="smart-farming-backend")
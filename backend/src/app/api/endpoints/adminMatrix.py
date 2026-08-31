from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

router = APIRouter()

@router.get("/admin/metrics", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def metrics_placeholder() -> dict[str, str]:
    raise HTTPException(status_code=501, detail="Metrics are scheduled for Stage 16.")
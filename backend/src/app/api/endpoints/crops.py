from __future__ import annotations

from fastapi import APIRouter

from app.schemas import CropListResponse

router = APIRouter()

@router.get("/crops", response_model=CropListResponse)
async def crops() -> CropListResponse:
    from app.pipeline import _CONFIG

    configured = _CONFIG.get("models", {}).get("disease_models", {})
    return CropListResponse(crops=sorted(str(crop) for crop in configured))

from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.schemas import FarmRequest, FarmResponse
from app.crud import get_user, save_farm
from app.core import get_session

router = APIRouter(prefix="/farm", tags=["farm"])

@router.get("", response_model=FarmResponse)
async def get_farmer_farm(
    user_id: str = Depends(get_current_user), session: Session = Depends(get_session)
) -> FarmResponse:
    try:
        user = get_user(session, user_id)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    if user is None or user.farm is None:
        raise HTTPException(status_code=404, detail="Farm has not been configured.")
    farm = user.farm
    return FarmResponse(
        id=farm.id,
        name=farm.name,
        location=farm.location,
        area_acres=farm.area_acres,
        latitude=farm.latitude,
        longitude=farm.longitude,
        crop_history=farm.crop_history or [],
    )

@router.put("", response_model=FarmResponse)
async def save_farmer_farm(
    payload: FarmRequest,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> FarmResponse:
    try:
        user = get_user(session, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="Farmer profile not found.")
        farm = save_farm(session, user, payload.model_dump())
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    return FarmResponse(
        id=farm.id,
        name=farm.name,
        location=farm.location,
        area_acres=farm.area_acres,
        latitude=farm.latitude,
        longitude=farm.longitude,
        crop_history=farm.crop_history or [],
    )


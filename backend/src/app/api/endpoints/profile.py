from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.schemas import ProfileResponse, ProfileUpdateRequest
from app.crud import get_user, update_profile
from app.core import get_session

router = APIRouter(prefix="/profile", tags=["profile"])

def _profile(user) -> ProfileResponse:
    farm = user.farm
    return ProfileResponse(
        id=user.id,
        name=user.name,
        phone=user.phone,
        email=user.email,
        language=user.language,
        role=user.role,
        location=farm.location if farm else None,
        latitude=farm.latitude if farm else None,
        longitude=farm.longitude if farm else None,
        crop_history=farm.crop_history if farm else [],
        farm_name=farm.name if farm else None,
        farm_area_acres=farm.area_acres if farm else None,
    )

@router.get("", response_model=ProfileResponse)
async def get_farmer_profile(
    user_id: str = Depends(get_current_user), session: Session = Depends(get_session)
) -> ProfileResponse:
    try:
        user = get_user(session, user_id)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    if user is None:
        raise HTTPException(status_code=404, detail="Farmer profile not found.")
    return _profile(user)

@router.patch("", response_model=ProfileResponse)
async def update_farmer_profile(
    payload: ProfileUpdateRequest,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ProfileResponse:
    try:
        user = get_user(session, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="Farmer profile not found.")
        user = update_profile(
            session,
            user,
            name=payload.name,
            language=payload.language,
            location=payload.location,
            latitude=payload.latitude,
            longitude=payload.longitude,
            crop_history=payload.crop_history,
        )
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    return _profile(user)


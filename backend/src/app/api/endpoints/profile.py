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

import re
from datetime import datetime, timedelta, timezone
from typing import Any

_PHONE_REGEX = re.compile(r"^\+?[0-9]{10,15}$")


@router.patch("", response_model=ProfileResponse)
async def update_farmer_profile(
    payload: ProfileUpdateRequest,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ProfileResponse:
    if payload.name is not None:
        trimmed = payload.name.strip()
        if len(trimmed) < 2 or len(trimmed) > 100:
            raise HTTPException(status_code=422, detail="Name must be between 2 and 100 characters.")

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


@router.delete("", status_code=200)
async def delete_farmer_profile(
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """30-day soft-delete for user account (GDPR compliance)."""
    user = get_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User profile not found.")
    purge_date = datetime.now(timezone.utc) + timedelta(days=30)
    user.deleted_at = purge_date
    session.add(user)
    session.commit()
    return {
        "status": "scheduled_for_deletion",
        "message": "Account scheduled for deletion with a 30-day grace period.",
        "purge_date": purge_date.isoformat(),
    }


@router.get("/export", status_code=200)
async def export_personal_data(
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Export all personal and agricultural data for the authenticated user as JSON."""
    user = get_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User profile not found.")
    
    farm_data = None
    if user.farm:
        farm = user.farm
        farm_data = {
            "name": farm.name,
            "location": farm.location,
            "area_acres": farm.area_acres,
            "latitude": farm.latitude,
            "longitude": farm.longitude,
            "crop_history": farm.crop_history,
            "boundary": farm.boundary,
            "plots": [
                {"id": p.id, "name": p.name, "crop": p.crop, "area_acres": p.area_acres, "status": p.status}
                for p in farm.plots
            ],
        }

    predictions_data = [
        {
            "id": p.id,
            "crop": p.crop,
            "disease": p.disease,
            "disease_conf": p.disease_conf,
            "severity_pct": p.severity_pct,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in user.predictions
    ]

    alerts_data = [
        {"id": a.id, "kind": a.kind, "title": a.title, "body": a.body, "is_read": a.is_read}
        for a in user.alerts
    ]

    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "language": user.language,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
        "farm": farm_data,
        "predictions": predictions_data,
        "alerts": alerts_data,
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }



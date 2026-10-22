from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.schemas import ProfileResponse, ProfileUpdateRequest
from app.crud import get_user, update_profile
from app.core import get_session
from app.services.translation.overlay import overlay_dict_translations
from app.models.translation import EntityTranslation

router = APIRouter(prefix="/profile", tags=["profile"])

def _profile(user) -> ProfileResponse:
    farm = user.farm
    return ProfileResponse(
        id=user.id,
        name=user.name,
        phone=user.phone,
        email=user.email,
        is_email_verified=getattr(user, "is_email_verified", False),
        pending_email=getattr(user, "pending_email", None),
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
    request: Request,
    lang: str | None = None,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ProfileResponse:
    try:
        user = get_user(session, user_id)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    if user is None:
        auth_header = request.headers.get("authorization", "")
        token_str = (
            auth_header.replace("Bearer ", "").strip()
            if auth_header.startswith("Bearer ")
            else ""
        )
        from app.api.endpoints.auth import fetch_supabase_user_details
        from app.crud.user import create_user, find_user_by_identifier, normalize_phone_number
        sup_details = await fetch_supabase_user_details(user_id, token_str)
        if sup_details or token_str:
            sup_meta = (sup_details or {}).get("user_metadata", {})
            sup_phone = normalize_phone_number((sup_details or {}).get("phone"))
            sup_email = ((sup_details or {}).get("email") or "").strip().lower() or None

            existing = None
            if sup_phone:
                existing = find_user_by_identifier(session, sup_phone)
            if not existing and sup_email:
                existing = find_user_by_identifier(session, sup_email)

            if existing is not None:
                if existing.id != user_id:
                    existing.id = user_id
                if sup_phone and not existing.phone:
                    existing.phone = sup_phone
                if sup_email and not existing.email:
                    existing.email = sup_email
                session.commit()
                session.refresh(existing)
                user = existing
            else:
                resolved_name = sup_meta.get("name") or (
                    f"Farmer {sup_phone[-4:]}" if sup_phone and len(sup_phone) >= 4 else "Farmer"
                )
                resolved_lang = sup_meta.get("language") or "English"
                resolved_loc = sup_meta.get("location") or "Gujarat, India"
                resolved_farm = sup_meta.get("farm_name") or f"{resolved_name}'s Farm"
                try:
                    user = create_user(
                        session,
                        user_id=user_id,
                        name=resolved_name,
                        phone=sup_phone,
                        email=sup_email,
                        password_hash=None,
                        language=resolved_lang,
                        location=resolved_loc,
                        crop_history=sup_meta.get("crop_history") or [],
                        farm_name=resolved_farm,
                    )
                except Exception as exc:
                    session.rollback()
                    raise HTTPException(status_code=404, detail="Farmer profile not found.") from exc
        else:
            raise HTTPException(status_code=404, detail="Farmer profile not found.")
    
    res = _profile(user)
    req_lang = lang or request.headers.get("accept-language") or user.language
    if req_lang and not req_lang.lower().startswith("en"):
        norm_code = "gu" if req_lang.lower().startswith("gu") else ("hi" if req_lang.lower().startswith("hi") else None)
        if norm_code:
            res_dict = res.model_dump()
            overlay_dict_translations(session, res_dict, "user", user.id, ["name"], norm_code, name_fields=["name"])
            if user.farm:
                farm_dict = {"name": user.farm.name, "location": user.farm.location or ""}
                overlay_dict_translations(session, farm_dict, "farm", user.farm.id, ["name", "location"], norm_code, name_fields=["name", "location"])
                if farm_dict.get("name"):
                    res_dict["farm_name"] = farm_dict["name"]
                if farm_dict.get("location"):
                    res_dict["location"] = farm_dict["location"]
            return ProfileResponse(**res_dict)
    return res

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

    clean_phone: str | None = None
    if payload.phone is not None:
        raw_phone = payload.phone.strip()
        if raw_phone:
            cleaned = re.sub(r"[\s\-\(\)\.]", "", raw_phone)
            if not _PHONE_REGEX.match(cleaned):
                raise HTTPException(
                    status_code=422,
                    detail="Please provide a valid 10 to 15 digit phone number (e.g. 9999999999 or +919999999999).",
                )
            clean_phone = cleaned

            from sqlalchemy import select
            from app.models import User
            digits = "".join(ch for ch in cleaned if ch.isdigit())
            last10 = digits[-10:] if len(digits) >= 10 else digits
            phone_variants = [cleaned, digits, f"+91{last10}"]
            existing = session.scalar(
                select(User).where(
                    User.id != user_id,
                    User.phone.in_(phone_variants),
                )
            )
            if existing:
                raise HTTPException(
                    status_code=409,
                    detail="This phone number is already registered to another account.",
                )

    try:
        user = get_user(session, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="Farmer profile not found.")

        if clean_phone and clean_phone != user.phone:
            raise HTTPException(
                status_code=400,
                detail="Mobile phone number cannot be updated directly. Please use the mobile verification workflow in Settings.",
            )

        user = update_profile(
            session,
            user,
            name=payload.name,
            phone=clean_phone if payload.phone is not None else None,
            language=payload.language,
            location=payload.location,
            latitude=payload.latitude,
            longitude=payload.longitude,
            crop_history=payload.crop_history,
            farm_name=payload.farm_name,
            farm_area_acres=payload.farm_area_acres,
        )

        # Sync updated phone with Supabase Auth via Admin API
        if clean_phone:
            from app.api.endpoints.auth import sync_supabase_user_phone
            try:
                await sync_supabase_user_phone(user.id, clean_phone)
            except Exception:
                pass

        # Enqueue write-time transliteration for user name
        if payload.name:
            from app.core.arq import enqueue_translation
            try:
                await enqueue_translation("user", user.id, {"name": payload.name}, name_fields=["name"])
            except Exception:
                pass
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    return _profile(user)


@router.delete("", status_code=200)
def delete_farmer_profile(
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
def export_personal_data(
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



from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.api.auth import create_token_pair, decode_token, hash_password, verify_password
from backend.api.deps import get_current_user
from backend.api.schemas import (
    AuthResponse,
    LoginRequest,
    ProfileResponse,
    ProfileUpdateRequest,
    RefreshRequest,
    RegisterRequest,
)
from backend.database.repository import create_user, find_user_by_identifier, get_user, update_profile
from backend.database.session import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


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
    )


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(payload: RegisterRequest, session: Session = Depends(get_session)) -> AuthResponse:
    if not payload.phone and not payload.email:
        raise HTTPException(status_code=422, detail="Provide a phone number or email address.")
    try:
        user = create_user(
            session,
            user_id=str(uuid.uuid4()),
            name=payload.name,
            phone=payload.phone,
            email=payload.email,
            password_hash=hash_password(payload.password),
            language=payload.language,
            location=payload.location,
            latitude=payload.latitude,
            longitude=payload.longitude,
            crop_history=payload.crop_history,
        )
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="Phone or email is already registered.") from exc
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    return AuthResponse(tokens=create_token_pair(user.id), user=_profile(user))


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, session: Session = Depends(get_session)) -> AuthResponse:
    try:
        user = find_user_by_identifier(session, payload.identifier)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    if user is None or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    return AuthResponse(tokens=create_token_pair(user.id), user=_profile(user))


@router.post("/refresh", response_model=dict[str, str | int])
async def refresh(payload: RefreshRequest) -> dict[str, str | int]:
    try:
        user_id = decode_token(payload.refresh_token, expected_type="refresh")
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return create_token_pair(user_id)


@router.get("/profile", response_model=ProfileResponse)
async def profile(user_id: str = Depends(get_current_user), session: Session = Depends(get_session)) -> ProfileResponse:
    try:
        user = get_user(session, user_id)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    if user is None:
        raise HTTPException(status_code=404, detail="Farmer profile not found.")
    return _profile(user)


@router.patch("/profile", response_model=ProfileResponse)
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

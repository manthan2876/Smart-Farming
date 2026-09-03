from __future__ import annotations

import uuid
from fastapi import APIRouter
from app.core.limiter import limiter
from fastapi import Depends, HTTPException, status, Response, Request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from app.api.deps import hash_password, verify_password, create_token_pair, decode_token
from app.schemas import (
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ProfileResponse
)
from app.crud import (
    create_user,
    find_user_by_identifier,
)
from app.core import get_session

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
        farm_name=farm.name if farm else None,
        farm_area_acres=farm.area_acres if farm else None,
    )

@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    payload: RegisterRequest, response: Response, session: Session = Depends(get_session)
) -> AuthResponse:
    if not payload.phone and not payload.email:
        raise HTTPException(
            status_code=422, detail="Provide a phone number or email address."
        )
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
            farm_name=payload.farm_name,
            farm_area_acres=payload.farm_area_acres,
        )
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="Phone or email is already registered."
        ) from exc
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
        
    tokens = create_token_pair(user.id)
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )
    return AuthResponse(tokens=tokens, user=_profile(user))


@router.post("/login", response_model=AuthResponse)
@limiter.limit("5/minute")
async def login(
    request: Request, payload: LoginRequest, response: Response, session: Session = Depends(get_session)
) -> AuthResponse:
    try:
        user = find_user_by_identifier(session, payload.identifier)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    if (
        user is None
        or not user.password_hash
        or not verify_password(payload.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
        )
    
    tokens = create_token_pair(user.id)
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )
    return AuthResponse(tokens=tokens, user=_profile(user))


@router.post("/refresh", response_model=dict[str, str | int])
async def refresh(request: Request, response: Response) -> dict[str, str | int]:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token.")
    try:
        user_id = decode_token(refresh_token, expected_type="refresh")
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
        
    tokens = create_token_pair(user_id)
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )
    return tokens


@router.post("/logout", response_model=dict[str, str])
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie("refresh_token", httponly=True, secure=False, samesite="lax")
    return {"status": "success"}

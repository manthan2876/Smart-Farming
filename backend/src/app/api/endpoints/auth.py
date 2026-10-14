import logging
import secrets
import uuid
from typing import Any
import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from app.core.limiter import limiter
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from app.api.deps import hash_password, verify_password, create_token_pair, decode_token, get_current_user
from app.core import get_session
from app.core.config import settings
from app.models import User
from app.schemas import (
    AuthResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    ProfileResponse,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
)
from app.crud import (
    create_user,
    find_user_by_identifier,
    create_password_reset_token,
    get_valid_password_reset_token,
    mark_token_used,
)
from app.services.email import send_reset_password_email

logger = logging.getLogger("smart-farming.auth")

router = APIRouter(prefix="/auth", tags=["auth"])


async def _sync_supabase_user_password(user_id: str, new_password: str) -> bool:
    """Updates the user's password in Supabase Auth via the Admin API."""
    supabase_url = getattr(settings, "SUPABASE_URL", "")
    service_key = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")
    if not supabase_url or not service_key or not user_id:
        return False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.put(
                f"{supabase_url.rstrip('/')}/auth/v1/admin/users/{user_id}",
                headers={
                    "apikey": service_key,
                    "Authorization": f"Bearer {service_key}",
                    "Content-Type": "application/json",
                },
                json={"password": new_password},
            )
            return resp.status_code in (200, 201)
    except Exception as exc:
        logger.warning("Failed to sync password to Supabase Auth for user %s: %s", user_id, exc)
        return False


async def _fetch_supabase_tokens(email: str, password: str) -> dict[str, Any] | None:
    """Acquires valid Supabase Auth tokens for a user using password grant."""
    supabase_url = getattr(settings, "SUPABASE_URL", "")
    anon_key = (
        getattr(settings, "SUPABASE_ANON_KEY", "")
        or getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")
    )
    if not supabase_url or not anon_key or not email:
        return None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{supabase_url.rstrip('/')}/auth/v1/token?grant_type=password",
                headers={
                    "apikey": anon_key,
                    "Content-Type": "application/json",
                },
                json={"email": email, "password": password},
            )
            if resp.status_code == 200:
                td = resp.json()
                return {
                    "access_token": td.get("access_token"),
                    "refresh_token": td.get("refresh_token"),
                    "token_type": td.get("token_type", "bearer"),
                    "expires_in": td.get("expires_in", 3600),
                }
    except Exception as exc:
        logger.warning("Failed to acquire Supabase tokens: %s", exc)
    return None

def _profile(user, session: Session | None = None, req_lang: str | None = None) -> ProfileResponse:
    farm = user.farm
    base = ProfileResponse(
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
    if not session:
        return base
    lang_to_use = req_lang or user.language
    if lang_to_use and not lang_to_use.lower().startswith("en"):
        norm_code = "gu" if lang_to_use.lower().startswith("gu") else ("hi" if lang_to_use.lower().startswith("hi") else None)
        if norm_code:
            from app.services.translation.overlay import overlay_dict_translations
            res_dict = base.model_dump()
            overlay_dict_translations(session, res_dict, "user", user.id, ["name"], norm_code, name_fields=["name"])
            if farm:
                farm_dict = {"name": farm.name, "location": farm.location or ""}
                overlay_dict_translations(session, farm_dict, "farm", farm.id, ["name", "location"], norm_code, name_fields=["name", "location"])
                if farm_dict.get("name"):
                    res_dict["farm_name"] = farm_dict["name"]
                if farm_dict.get("location"):
                    res_dict["location"] = farm_dict["location"]
            return ProfileResponse(**res_dict)
    return base


@router.post("/change-password", response_model=MessageResponse, status_code=200)
@limiter.limit("5/minute")
async def change_password(
    request: Request,
    payload: ChangePasswordRequest,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> MessageResponse:
    """Change password for the authenticated user."""
    if payload.new_password == payload.old_password:
        raise HTTPException(
            status_code=400,
            detail="New password cannot be the same as your current password.",
        )
    user = session.get(User, user_id)
    if not user or not user.password_hash:
        raise HTTPException(status_code=404, detail="User not found.")
    if not verify_password(payload.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    user.password_hash = hash_password(payload.new_password)
    session.add(user)
    session.commit()
    await _sync_supabase_user_password(user.id, payload.new_password)
    return MessageResponse(status="success", message="Password changed successfully.")


@router.post("/forgot-password", response_model=MessageResponse, status_code=200)
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
) -> MessageResponse:
    """
    Request a password reset link.
    Anti-enumeration protection: always returns the same generic message.
    """
    target_email = payload.email.strip().lower()
    user = session.query(User).filter(User.email.ilike(target_email)).first()
    if user and user.email:
        raw_token = secrets.token_urlsafe(32)
        create_password_reset_token(
            session, user_id=user.id, raw_token=raw_token, expires_in_minutes=15
        )
        background_tasks.add_task(send_reset_password_email, email_to=user.email, token=raw_token)

    return MessageResponse(
        status="success",
        message="If an account with that email exists, a password reset link has been sent to your email address.",
    )


@router.post("/reset-password", response_model=MessageResponse, status_code=200)
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    payload: ResetPasswordRequest,
    session: Session = Depends(get_session),
) -> MessageResponse:
    """
    Reset password using a valid, non-expired, single-use token.
    """
    token_record = get_valid_password_reset_token(session, payload.token)
    if not token_record:
        raise HTTPException(
            status_code=400,
            detail="Password reset token is invalid or has expired. Please request a new link.",
        )
    user = session.get(User, token_record.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.password_hash = hash_password(payload.new_password)
    mark_token_used(session, token_record)
    session.add(user)
    session.commit()
    await _sync_supabase_user_password(user.id, payload.new_password)
    return MessageResponse(
        status="success",
        message="Password has been reset successfully. You can now log in.",
    )


def _cookie_settings(request: Request | None = None) -> dict[str, Any]:
    """Determine cookie Secure and SameSite attributes.

    In production or across HTTPS cross-site origins (e.g. Vercel frontend calling Render backend),
    cookies MUST use SameSite=None and Secure=True to be accepted by modern browsers.
    In local HTTP development, SameSite=Lax and Secure=False avoids browser rejection.
    """
    is_prod = getattr(settings, "ENVIRONMENT", "development") == "production"
    is_https = False
    if request:
        proto = request.headers.get("x-forwarded-proto") or request.url.scheme
        origin = request.headers.get("origin", "")
        is_https = proto == "https" or origin.startswith("https://")

    if is_prod or is_https:
        return {"secure": True, "samesite": "none"}
    return {"secure": False, "samesite": "lax"}


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    request: Request, payload: RegisterRequest, response: Response, session: Session = Depends(get_session)
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
    cookie_opts = _cookie_settings(request)
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=cookie_opts["secure"],
        samesite=cookie_opts["samesite"],
        max_age=30 * 24 * 60 * 60,
    )

    # Enqueue write-time transliteration for user and farm name
    from app.core.arq import enqueue_translation
    try:
        await enqueue_translation("user", user.id, {"name": user.name}, name_fields=["name"])
        if user.farm:
            await enqueue_translation(
                "farm",
                user.farm.id,
                {"name": user.farm.name, "location": user.farm.location or ""},
                name_fields=["name", "location"],
            )
    except Exception:
        pass

    return AuthResponse(tokens=tokens, user=_profile(user, session=session))


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
    
    # Synchronize password with Supabase Auth and fetch Supabase tokens
    supabase_tokens = None
    if user.email:
        await _sync_supabase_user_password(user.id, payload.password)
        supabase_tokens = await _fetch_supabase_tokens(user.email, payload.password)

    tokens = supabase_tokens or create_token_pair(user.id)
    cookie_opts = _cookie_settings(request)
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=cookie_opts["secure"],
        samesite=cookie_opts["samesite"],
        max_age=30 * 24 * 60 * 60,
    )
    return AuthResponse(
        tokens=tokens,
        user=_profile(user, session=session, req_lang=request.headers.get("accept-language")),
    )


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
    cookie_opts = _cookie_settings(request)
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=cookie_opts["secure"],
        samesite=cookie_opts["samesite"],
        max_age=30 * 24 * 60 * 60,
    )
    return tokens


@router.post("/logout", response_model=dict[str, str])
async def logout(request: Request, response: Response) -> dict[str, str]:
    cookie_opts = _cookie_settings(request)
    response.delete_cookie(
        "refresh_token",
        httponly=True,
        secure=cookie_opts["secure"],
        samesite=cookie_opts["samesite"],
    )
    return {"status": "success"}


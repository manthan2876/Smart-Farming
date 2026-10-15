import logging
import secrets
import uuid
from typing import Any
import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from app.core.limiter import limiter
from sqlalchemy import func, or_, text
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
    SessionSyncRequest,
    RequestEmailUpdateRequest,
    RequestPhoneUpdateRequest,
    VerifyPhoneUpdateRequest,
    VerifyEmailRequest,
    ResendVerificationEmailRequest,
    SetupFirstTimePasswordRequest,
)
from app.crud import (
    create_user,
    find_user_by_identifier,
    create_password_reset_token,
    get_valid_password_reset_token,
    mark_token_used,
    create_email_verification_token,
    get_valid_email_verification_token,
    mark_email_verification_token_used,
)
from app.services.email import send_reset_password_email, send_verification_email

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


async def sync_supabase_user_phone(user_id: str, phone: str) -> bool:
    """Updates the user's phone in Supabase Auth via Admin API without triggering verification SMS."""
    supabase_url = getattr(settings, "SUPABASE_URL", "")
    service_key = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")
    if not supabase_url or not service_key or not user_id or not phone:
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
                json={
                    "phone": phone,
                    "phone_confirm": True,
                    "user_metadata": {"phone": phone},
                },
            )
            if resp.status_code in (200, 201):
                logger.info("Successfully synced phone %s for user %s to Supabase Auth", phone, user_id)
                return True
            else:
                logger.warning("Supabase Auth admin update phone returned %s: %s", resp.status_code, resp.text)
                return False
    except Exception as exc:
        logger.warning("Failed to sync phone to Supabase Auth for user %s: %s", user_id, exc)
        return False


async def verify_supabase_phone_otp(phone: str, token: str) -> bool:
    """Verifies an SMS OTP token against Supabase GoTrue API."""
    supabase_url = getattr(settings, "SUPABASE_URL", "")
    anon_key = (
        getattr(settings, "SUPABASE_ANON_KEY", "")
        or getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")
    )
    if not supabase_url or not anon_key or not phone or not token:
        return False
    digits = "".join(ch for ch in phone if ch.isdigit())
    last10 = digits[-10:] if len(digits) >= 10 else digits
    candidates = [phone]
    if digits and digits not in candidates:
        candidates.append(digits)
    if last10 and len(last10) == 10:
        p91 = f"+91{last10}"
        if p91 not in candidates:
            candidates.append(p91)
        if last10 not in candidates:
            candidates.append(last10)

    for cand in candidates:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    f"{supabase_url.rstrip('/')}/auth/v1/verify",
                    headers={
                        "apikey": anon_key,
                        "Authorization": f"Bearer {anon_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "type": "sms",
                        "phone": cand,
                        "token": token.strip(),
                    },
                )
                if resp.status_code in (200, 201):
                    logger.info("Supabase phone OTP successfully verified for candidate %s", cand)
                    return True
                else:
                    logger.debug("Candidate %s verify returned %s: %s", cand, resp.status_code, resp.text)
        except Exception as exc:
            logger.warning("Supabase phone OTP verify error for %s: %s", cand, exc)
    return False


async def sync_supabase_user_email(user_id: str, email: str) -> bool:
    """Updates the user's email in Supabase Auth via Admin API as confirmed."""
    supabase_url = getattr(settings, "SUPABASE_URL", "")
    service_key = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")
    if not supabase_url or not service_key or not user_id or not email:
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
                json={
                    "email": email,
                    "email_confirm": True,
                    "user_metadata": {"email": email},
                },
            )
            if resp.status_code in (200, 201):
                logger.info("Successfully synced email %s for user %s to Supabase Auth", email, user_id)
                return True
            else:
                logger.warning("Supabase Auth admin update email returned %s: %s", resp.status_code, resp.text)
                return False
    except Exception as exc:
        logger.warning("Failed to sync email to Supabase Auth for user %s: %s", user_id, exc)
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


async def fetch_supabase_user_details(user_id: str, bearer_token: str | None = None) -> dict[str, Any] | None:
    """Fetches user details from Supabase Auth via Admin API or User endpoint."""
    supabase_url = getattr(settings, "SUPABASE_URL", "")
    service_key = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")
    anon_key = (
        getattr(settings, "SUPABASE_ANON_KEY", "")
        or getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")
    )
    if not supabase_url:
        return None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            if service_key:
                resp = await client.get(
                    f"{supabase_url.rstrip('/')}/auth/v1/admin/users/{user_id}",
                    headers={
                        "apikey": service_key,
                        "Authorization": f"Bearer {service_key}",
                    },
                )
                if resp.status_code == 200:
                    return resp.json()
            if bearer_token and anon_key:
                resp = await client.get(
                    f"{supabase_url.rstrip('/')}/auth/v1/user",
                    headers={
                        "apikey": anon_key,
                        "Authorization": f"Bearer {bearer_token}",
                    },
                )
                if resp.status_code == 200:
                    return resp.json()
    except Exception as exc:
        logger.warning("Failed to fetch Supabase user details for %s: %s", user_id, exc)
    return None


def _profile(user, session: Session | None = None, req_lang: str | None = None) -> ProfileResponse:
    farm = user.farm
    base = ProfileResponse(
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
    request: Request,
    payload: RegisterRequest,
    response: Response,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
) -> AuthResponse:
    from app.crud.user import normalize_phone_number
    clean_email = payload.email.strip().lower() if payload.email and payload.email.strip() else None
    clean_phone = normalize_phone_number(payload.phone)

    if not clean_phone and not clean_email:
        raise HTTPException(
            status_code=422, detail="Provide a phone number or email address."
        )

    if clean_email:
        existing_email_user = session.query(User).filter(
            func.lower(User.email) == clean_email
        ).first()
        if existing_email_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This email address is already registered to an account.",
            )

    if clean_phone:
        existing_phone_user = find_user_by_identifier(session, clean_phone)
        if existing_phone_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This phone number is already registered to an account.",
            )

    is_email_reg = bool(clean_email)
    try:
        user = create_user(
            session,
            user_id=str(uuid.uuid4()),
            name=payload.name,
            phone=clean_phone,
            email=clean_email,
            password_hash=hash_password(payload.password),
            language=payload.language,
            location=payload.location,
            latitude=payload.latitude,
            longitude=payload.longitude,
            crop_history=payload.crop_history,
            farm_name=payload.farm_name,
            farm_area_acres=payload.farm_area_acres,
            is_email_verified=False if is_email_reg else True,
            email_verified_at=None if is_email_reg else datetime.now(timezone.utc),
        )
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="Phone or email is already registered."
        ) from exc
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc

    if is_email_reg and user.email:
        raw_token = secrets.token_urlsafe(32)
        create_email_verification_token(
            session,
            user_id=user.id,
            pending_email=user.email,
            raw_token=raw_token,
            token_type="registration",
            expires_in_hours=24,
        )
        background_tasks.add_task(
            send_verification_email,
            email_to=user.email,
            token=raw_token,
            token_type="registration",
            user_name=user.name,
            user_id=user.id,
            phone=user.phone,
            language=user.language,
            location=payload.location,
        )
        if clean_phone:
            background_tasks.add_task(sync_supabase_user_phone, user.id, clean_phone)
        tokens = {
            "access_token": "",
            "refresh_token": "",
            "token_type": "bearer",
            "expires_in": 0,
            "verification_required": True,
        }
    else:
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
@limiter.limit("10/minute")
async def login(
    request: Request, payload: LoginRequest, response: Response, session: Session = Depends(get_session)
) -> AuthResponse:
    try:
        user = find_user_by_identifier(session, payload.identifier)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
        )

    clean_id = payload.identifier.strip().lower()
    is_pending_email_attempt = bool(user.pending_email and clean_id == user.pending_email.lower())
    is_email_attempt = bool((user.email and clean_id == user.email.lower()) or is_pending_email_attempt)

    if is_email_attempt:
        # 1. Require verified email
        if not user.is_email_verified or is_pending_email_attempt:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email is not verified. Please check your inbox for the verification link or request a new one.",
            )

        # 2. Check if phone-registered user without password (first-time email login)
        if not user.password_hash and user.phone:
            masked = f"+91******{user.phone[-4:]}" if len(user.phone) >= 4 else user.phone
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FIRST_TIME_EMAIL_OTP_REQUIRED",
                    "message": "First-time email login requires mobile verification. An OTP has been sent to your registered mobile phone.",
                    "phone": user.phone,
                    "masked_phone": masked,
                    "email": user.email,
                },
            )

    # 3. Standard password verification
    if (
        not user.password_hash
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


@router.post("/request-email-update", response_model=MessageResponse, status_code=200)
@limiter.limit("5/minute")
async def request_email_update(
    request: Request,
    payload: RequestEmailUpdateRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> MessageResponse:
    """
    Request to add or update an email address for an authenticated user (e.g. phone signed-in user).
    Sends a verification link to the target email address.
    """
    target_email = payload.email.strip().lower()
    if "@" not in target_email or "." not in target_email.split("@")[-1]:
        raise HTTPException(status_code=422, detail="Please enter a valid email address.")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if user.email and user.email.lower() == target_email and user.is_email_verified:
        raise HTTPException(status_code=400, detail="This email is already linked and verified on your account.")

    # Check if email is already taken by another account
    existing = session.query(User).filter(
        User.email.ilike(target_email),
        User.id != user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="This email address is already linked to another account.")

    user.pending_email = target_email
    session.add(user)

    raw_token = secrets.token_urlsafe(32)
    create_email_verification_token(
        session,
        user_id=user.id,
        pending_email=target_email,
        raw_token=raw_token,
        token_type="email_update",
        expires_in_hours=24,
    )
    session.commit()

    background_tasks.add_task(
        send_verification_email,
        email_to=target_email,
        token=raw_token,
        token_type="email_update",
        user_name=user.name,
        user_id=user.id,
    )

    return MessageResponse(
        status="success",
        message="A verification link has been sent to your email address. Please click the link to confirm.",
    )


@router.post("/request-phone-update", response_model=MessageResponse, status_code=200)
@limiter.limit("5/minute")
async def request_phone_update(
    request: Request,
    payload: RequestPhoneUpdateRequest,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> MessageResponse:
    """
    Validate that the requested mobile phone number is valid and not already
    registered to another account before sending an SMS verification OTP.
    """
    from app.crud.user import normalize_phone_number
    clean_phone = normalize_phone_number(payload.phone)
    if not clean_phone or len(clean_phone) < 10:
        raise HTTPException(
            status_code=422,
            detail="Please provide a valid 10 to 15 digit mobile phone number.",
        )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if user.phone == clean_phone:
        raise HTTPException(
            status_code=400,
            detail="This mobile number is already linked to your account.",
        )

    existing = find_user_by_identifier(session, clean_phone)
    if existing and existing.id != user.id:
        raise HTTPException(
            status_code=409,
            detail="This phone number is already registered to another account.",
        )

    return MessageResponse(
        status="success",
        message="Phone number is available for linking.",
    )


@router.post("/verify-phone-update", response_model=ProfileResponse, status_code=200)
@limiter.limit("5/minute")
async def verify_phone_update(
    request: Request,
    payload: VerifyPhoneUpdateRequest,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ProfileResponse:
    """
    Verify the phone number and link it to the user's account, then sync with Supabase Auth.
    """
    from app.crud.user import normalize_phone_number
    clean_phone = normalize_phone_number(payload.phone)
    if not clean_phone or len(clean_phone) < 10:
        raise HTTPException(
            status_code=422,
            detail="Please provide a valid mobile phone number.",
        )

    clean_token = payload.token.strip() if payload.token else ""
    if not clean_token or len(clean_token) < 6:
        raise HTTPException(
            status_code=422,
            detail="Please enter the complete 6-digit verification code.",
        )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # 1. Verify OTP:
    is_valid_otp = False
    if payload.verified_phone_token:
        from app.api.deps import _verify_supabase_token
        supa_uid = _verify_supabase_token(payload.verified_phone_token)
        if supa_uid:
            is_valid_otp = True

    if not is_valid_otp:
        is_valid_otp = await verify_supabase_phone_otp(clean_phone, clean_token)

    if not is_valid_otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification code. Please check the code and try again.",
        )

    # 2. Clean up any temporary orphan users created without email during OTP dispatch
    clean_phone_digits = "".join(ch for ch in clean_phone if ch.isdigit())
    last10 = clean_phone_digits[-10:] if len(clean_phone_digits) >= 10 else clean_phone_digits
    candidates = [clean_phone, f"+91{last10}", last10, clean_phone_digits]

    orphans = session.query(User).filter(
        User.id != user.id,
        User.phone.in_(candidates),
        or_(User.email.is_(None), User.email == ""),
    ).all()
    for orphan in orphans:
        orphan_id = orphan.id
        session.delete(orphan)
        try:
            session.execute(
                text("DELETE FROM auth.users WHERE id = :oid AND (email IS NULL OR email = '')"),
                {"oid": orphan_id},
            )
        except Exception as e:
            logger.warning("Could not delete orphan auth.users %s: %s", orphan_id, e)
    session.flush()

    try:
        session.execute(
            text(
                "DELETE FROM auth.users WHERE (phone = :p OR phone = :digits OR phone = :last10) "
                "AND id != :uid AND (email IS NULL OR email = '')"
            ),
            {"p": clean_phone, "digits": clean_phone_digits, "last10": last10, "uid": user.id},
        )
    except Exception as e:
        logger.warning("Could not clear auth.users phone conflict: %s", e)

    # 3. Ensure phone does not belong to another real account
    existing = find_user_by_identifier(session, clean_phone)
    if existing and existing.id != user.id:
        raise HTTPException(
            status_code=409,
            detail="This phone number is already registered to another account.",
        )

    # 4. Link verified phone to user
    user.phone = clean_phone
    session.add(user)
    session.commit()
    session.refresh(user)

    # 5. Sync confirmed phone to Supabase Auth so user can log in with either provider
    await sync_supabase_user_phone(user.id, clean_phone)

    return _profile(user, session=session, req_lang=request.headers.get("accept-language"))


@router.post("/verify-email", response_model=MessageResponse, status_code=200)
@limiter.limit("10/minute")
async def verify_email(
    request: Request,
    payload: VerifyEmailRequest,
    session: Session = Depends(get_session),
) -> MessageResponse:
    """
    Verify email address using a valid verification token from the email link.
    """
    token_record = get_valid_email_verification_token(session, payload.token)
    if not token_record:
        # Check if caller was redirected from Supabase Auth verification link with session token
        auth_header = request.headers.get("authorization") or ""
        bearer_token = (
            auth_header.replace("Bearer ", "").strip()
            if auth_header.startswith("Bearer ")
            else (payload.token if payload.token and len(payload.token) > 40 else "")
        )
        user = None
        if bearer_token:
            from app.api.deps import _verify_supabase_token
            supa_uid = await _verify_supabase_token(bearer_token)
            if supa_uid:
                user = session.get(User, supa_uid)

        if not user:
            raise HTTPException(
                status_code=400,
                detail="Verification link is invalid or has expired. Please request a new link.",
            )

        if user.pending_email:
            user.email = user.pending_email
            user.pending_email = None
        user.is_email_verified = True
        user.email_verified_at = datetime.now(timezone.utc)
        session.add(user)
        session.commit()
        return MessageResponse(
            status="success",
            message="Email verified successfully! Your email is now linked to your account.",
        )

    user = session.get(User, token_record.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    verified_email = token_record.pending_email
    user.email = verified_email
    user.pending_email = None
    user.is_email_verified = True
    user.email_verified_at = datetime.now(timezone.utc)

    mark_email_verification_token_used(session, token_record)
    session.add(user)
    session.commit()

    # Sync email to Supabase Auth admin
    await sync_supabase_user_email(user.id, verified_email)

    return MessageResponse(
        status="success",
        message="Email verified successfully! Your email is now linked to your account.",
    )


@router.post("/resend-verification-email", response_model=MessageResponse, status_code=200)
@limiter.limit("3/minute")
async def resend_verification_email(
    request: Request,
    payload: ResendVerificationEmailRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
) -> MessageResponse:
    """
    Resend verification email link for unverified email or pending update.
    Anti-enumeration protection: always returns success.
    """
    target_email = payload.email.strip().lower()
    user = session.query(User).filter(
        (User.email.ilike(target_email)) | (User.pending_email.ilike(target_email))
    ).first()

    if user:
        token_type = "email_update" if (user.pending_email and user.pending_email.lower() == target_email) else "registration"
        raw_token = secrets.token_urlsafe(32)
        create_email_verification_token(
            session,
            user_id=user.id,
            pending_email=target_email,
            raw_token=raw_token,
            token_type=token_type,
            expires_in_hours=24,
        )
        background_tasks.add_task(
            send_verification_email,
            email_to=target_email,
            token=raw_token,
            token_type=token_type,
            user_name=user.name,
            user_id=user.id,
        )

    return MessageResponse(
        status="success",
        message="If this email is associated with an unverified account, a new verification link has been sent.",
    )


@router.post("/setup-first-time-password", response_model=AuthResponse)
@limiter.limit("5/minute")
async def setup_first_time_password(
    request: Request,
    payload: SetupFirstTimePasswordRequest,
    response: Response,
    session: Session = Depends(get_session),
) -> AuthResponse:
    """
    Sets the password for a phone-registered user logging in via email for the first time
    after verifying their mobile OTP. Future logins will only require this password.
    """
    clean_email = payload.email.strip().lower()
    user = session.query(User).filter(User.email.ilike(clean_email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")

    if not user.is_email_verified:
        raise HTTPException(status_code=403, detail="Email address has not been verified.")

    # Validate phone match
    digits_input = "".join(ch for ch in payload.phone if ch.isdigit())
    digits_user = "".join(ch for ch in (user.phone or "") if ch.isdigit())
    if not digits_user or (digits_input[-10:] != digits_user[-10:]):
        raise HTTPException(status_code=400, detail="Phone number does not match account records.")

    # Set password
    user.password_hash = hash_password(payload.new_password)
    session.add(user)
    session.commit()
    session.refresh(user)

    # Sync password to Supabase Auth
    await _sync_supabase_user_password(user.id, payload.new_password)
    supabase_tokens = await _fetch_supabase_tokens(user.email, payload.new_password)

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


@router.post("/sync-session", response_model=AuthResponse)
async def sync_session(
    request: Request,
    payload: SessionSyncRequest,
    response: Response,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> AuthResponse:
    """Synchronize user profile into backend database from Supabase Phone / OAuth session."""
    auth_header = request.headers.get("authorization", "")
    token_str = (
        auth_header.replace("Bearer ", "").strip()
        if auth_header.startswith("Bearer ")
        else ""
    )

    # Fetch user details from Supabase Auth
    sup_details = await fetch_supabase_user_details(user_id, token_str)
    sup_meta = (sup_details or {}).get("user_metadata", {})
    from app.crud.user import normalize_phone_number
    sup_phone = normalize_phone_number((sup_details or {}).get("phone") or payload.phone)
    sup_email = ((sup_details or {}).get("email") or "").strip().lower() or None

    user = session.get(User, user_id)
    if user is None:
        # Check if an existing account exists with this phone or email
        existing = None
        if sup_phone:
            existing = find_user_by_identifier(session, sup_phone)
        if not existing and sup_email:
            existing = find_user_by_identifier(session, sup_email)

        if existing is not None:
            if existing.id != user_id:
                old_id = existing.id
                existing.id = user_id
                logger.info("Relinked existing user %s -> %s for session sync (%s)", old_id, user_id, sup_phone)
            if sup_phone and not existing.phone:
                existing.phone = sup_phone
            if sup_email and not existing.email:
                existing.email = sup_email
            session.commit()
            session.refresh(existing)
            user = existing
        else:
            resolved_name = (
                payload.name
                or sup_meta.get("name")
                or (f"Farmer {sup_phone[-4:]}" if sup_phone and len(sup_phone) >= 4 else "Farmer")
            )
            resolved_lang = payload.language or sup_meta.get("language") or "English"
            resolved_loc = payload.location or sup_meta.get("location") or "Gujarat, India"
            resolved_farm_name = payload.farm_name or sup_meta.get("farm_name") or f"{resolved_name}'s Farm"
            resolved_crop_history = payload.crop_history or sup_meta.get("crop_history") or []

            user = create_user(
                session,
                user_id=user_id,
                name=resolved_name,
                phone=sup_phone,
                email=sup_email,
                password_hash=None,
                language=resolved_lang,
                location=resolved_loc,
                crop_history=resolved_crop_history,
                farm_name=resolved_farm_name,
            )
    else:
        if payload.name:
            user.name = payload.name
        if sup_phone and not user.phone:
            user.phone = sup_phone
        if payload.language:
            user.language = payload.language
        if user.farm:
            if payload.location:
                user.farm.location = payload.location
            if payload.farm_name:
                user.farm.name = payload.farm_name
            if payload.crop_history:
                user.farm.crop_history = payload.crop_history
        session.commit()
        session.refresh(user)

    tokens = {
        "access_token": token_str or create_token_pair(user.id)["access_token"],
        "refresh_token": "",
        "token_type": "bearer",
        "expires_in": 3600,
    }
    return AuthResponse(
        tokens=tokens,
        user=_profile(user, session=session, req_lang=request.headers.get("accept-language")),
    )


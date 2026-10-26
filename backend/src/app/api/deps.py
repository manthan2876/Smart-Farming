from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from pwdlib import PasswordHash

_PASSWORD_HASH = PasswordHash.recommended()
_ALGORITHM = "HS256"
_ACCESS_MINUTES = 30
_REFRESH_DAYS = 30


from app.core.config import settings

def _secret_key() -> str:
    key = getattr(settings, "JWT_SECRET_KEY", None) or os.getenv("JWT_SECRET_KEY", "change-this-development-secret-key-32-bytes")
    env = getattr(settings, "ENVIRONMENT", "development").strip().lower()
    insecure_keys = (
        "change-this-development-secret-key-32-bytes",
        "dev-secret-key-change-me",
        "replace_with_a_long_random_jwt_secret_key",
        "generate_strong_64_character_random_hex_key_for_production",
    )
    if env in ("production", "staging") and (key in insecure_keys or len(key) < 32):
        raise RuntimeError("FATAL: Insecure or default JWT_SECRET_KEY detected in production/staging environment.")
    return key


def hash_password(password: str) -> str:
    return _PASSWORD_HASH.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _PASSWORD_HASH.verify(password, password_hash)


def create_token(user_id: str, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": user_id,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(payload, _secret_key(), algorithm=_ALGORITHM)


def create_token_pair(user_id: str) -> dict[str, Any]:
    return {
        "access_token": create_token(
            user_id, "access", timedelta(minutes=_ACCESS_MINUTES)
        ),
        "refresh_token": create_token(
            user_id, "refresh", timedelta(days=_REFRESH_DAYS)
        ),
        "token_type": "bearer",
        "expires_in": _ACCESS_MINUTES * 60,
    }


import time
import logging
import httpx

logger = logging.getLogger("smart-farming.auth")

_SUPABASE_USER_CACHE: dict[str, tuple[str, float]] = {}


def _verify_supabase_token(token: str) -> str | None:
    """Verifies a Supabase-issued JWT access token, supporting local secret or Supabase REST check."""
    # 1. Local signature verification if SUPABASE_JWT_SECRET is provided
    jwt_secret = getattr(settings, "SUPABASE_JWT_SECRET", None) or os.getenv("SUPABASE_JWT_SECRET")
    if jwt_secret:
        try:
            payload = jwt.decode(
                token,
                jwt_secret,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
            sub = payload.get("sub")
            if sub:
                return str(sub)
        except jwt.PyJWTError:
            # Fall back to local in-memory token cache or remote validation
            pass

    # 2. Check local in-memory token cache
    now = time.time()
    if token in _SUPABASE_USER_CACHE:
        user_id, exp_ts = _SUPABASE_USER_CACHE[token]
        if exp_ts > now:
            return user_id
        else:
            _SUPABASE_USER_CACHE.pop(token, None)

    # 3. Verify via Supabase Auth API
    supabase_url = getattr(settings, "SUPABASE_URL", "") or os.getenv("SUPABASE_URL", "")
    anon_key = (
        getattr(settings, "SUPABASE_ANON_KEY", "")
        or getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")
        or os.getenv("SUPABASE_ANON_KEY", "")
    )
    if supabase_url and anon_key:
        try:
            url = f"{supabase_url.rstrip('/')}/auth/v1/user"
            headers = {
                "Authorization": f"Bearer {token}",
                "apikey": anon_key,
            }
            with httpx.Client(timeout=4.0) as client:
                resp = client.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    user_id = data.get("id")
                    if user_id:
                        _SUPABASE_USER_CACHE[token] = (str(user_id), now + 60.0)
                        return str(user_id)
        except Exception as exc:
            logger.warning("Supabase auth API verification failed: %s", exc)

    return None


def decode_token(token: str, expected_type: str = "access") -> str:
    # 1. Check Supabase-issued authentication token
    supabase_user_id = _verify_supabase_token(token)
    if supabase_user_id:
        return supabase_user_id

    # 2. Legacy backend JWT verification
    try:
        payload = jwt.decode(token, _secret_key(), algorithms=[_ALGORITHM])
        if payload.get("sub"):
            if payload.get("type") == expected_type or payload.get("aud") == "authenticated":
                return str(payload["sub"])
    except jwt.PyJWTError:
        # Fall through to reject invalid token
        pass

    raise ValueError("Invalid or expired token.")


_BEARER = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_BEARER),
    x_user_id: str | None = Header(default=None),
) -> str:
    """Resolve a JWT user, strictly rejecting X-User-ID in production and staging."""
    if credentials is not None:
        try:
            return decode_token(credentials.credentials)
        except ValueError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    env = getattr(settings, "ENVIRONMENT", "development").strip().lower()
    if env in ("production", "staging") and x_user_id:
        logger.error("SECURITY: Rejected X-User-ID header attempt in production/staging environment.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header-based user impersonation (X-User-ID) is strictly forbidden in production.",
        )

    if env in ("development", "test") and getattr(settings, "DEBUG", True):
        if x_user_id and x_user_id.strip():
            logger.warning("AUTH: Bypassing JWT auth via X-User-ID header for user '%s' (allowed in development/test only)", x_user_id.strip())
            return x_user_id.strip()

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="A valid bearer access token is required.",
    )


from app.core import get_session
from app.crud import get_user
from sqlalchemy.orm import Session

def require_expert_role(
    user_id: str = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> str:
    user = get_user(session, user_id)
    if not user or user.role not in ["expert", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized. Expert role required.")
    return user_id

def require_admin_role(
    user_id: str = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> str:
    user = get_user(session, user_id)
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized. Admin role required.")
    return user_id

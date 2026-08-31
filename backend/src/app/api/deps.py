from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import os
from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from pwdlib import PasswordHash

_PASSWORD_HASH = PasswordHash.recommended()
_ALGORITHM = "HS256"
_ACCESS_MINUTES = 30
_REFRESH_DAYS = 30


def _secret_key() -> str:
    return os.getenv("JWT_SECRET_KEY", "change-this-development-secret-key-32-bytes")


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


def decode_token(token: str, expected_type: str = "access") -> str:
    try:
        payload = jwt.decode(token, _secret_key(), algorithms=[_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise ValueError("Invalid or expired token.") from exc
    if payload.get("type") != expected_type or not payload.get("sub"):
        raise ValueError("Invalid token type.")
    return str(payload["sub"])


_BEARER = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_BEARER),
    x_user_id: str | None = Header(default=None),
) -> str:
    """Resolve a JWT user, retaining X-User-ID only as a development fallback."""
    if credentials is not None:
        try:
            return decode_token(credentials.credentials)
        except ValueError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
    if not x_user_id or not x_user_id.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A bearer access token is required.",
        )
    return x_user_id.strip()

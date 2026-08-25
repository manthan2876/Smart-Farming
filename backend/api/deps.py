from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.api.auth import decode_token

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

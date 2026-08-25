from __future__ import annotations

from fastapi import Header, HTTPException, status


def get_current_user(x_user_id: str | None = Header(default=None)) -> str:
    """Temporary Stage 10 identity until JWT auth is implemented in Stage 12."""
    if not x_user_id or not x_user_id.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-ID header is required until Stage 12 authentication is added.",
        )
    return x_user_id.strip()

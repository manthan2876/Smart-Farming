from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.models.password_reset import PasswordResetToken


def hash_token(raw_token: str) -> str:
    """Return SHA-256 hex digest of the raw token."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_password_reset_token(
    session: Session,
    *,
    user_id: str,
    raw_token: str,
    expires_in_minutes: int = 15,
) -> PasswordResetToken:
    """
    Invalidate previous tokens for user and create a new hashed password reset token.
    """
    now = datetime.now(timezone.utc)
    # Invalidate previous unused tokens for this user
    session.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user_id,
        PasswordResetToken.used_at.is_(None),
    ).update({"used_at": now}, synchronize_session=False)

    token_record = PasswordResetToken(
        user_id=user_id,
        token_hash=hash_token(raw_token),
        expires_at=now + timedelta(minutes=expires_in_minutes),
        created_at=now,
    )
    session.add(token_record)
    session.commit()
    session.refresh(token_record)
    return token_record


def get_valid_password_reset_token(
    session: Session, raw_token: str
) -> PasswordResetToken | None:
    """
    Retrieve token if it matches hash, has not been used, and has not expired.
    """
    token_hash = hash_token(raw_token)
    now = datetime.now(timezone.utc)
    return (
        session.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > now,
        )
        .first()
    )


def mark_token_used(session: Session, token: PasswordResetToken) -> None:
    """Mark a token as consumed."""
    token.used_at = datetime.now(timezone.utc)
    session.add(token)
    session.commit()


def invalidate_user_reset_tokens(session: Session, user_id: str) -> None:
    """Invalidate all pending tokens for a user."""
    session.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user_id,
        PasswordResetToken.used_at.is_(None),
    ).update({"used_at": datetime.now(timezone.utc)}, synchronize_session=False)
    session.commit()

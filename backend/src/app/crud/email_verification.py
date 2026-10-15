from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.models.email_verification import EmailVerificationToken


def hash_token(raw_token: str) -> str:
    """Return SHA-256 hex digest of the raw verification token."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_email_verification_token(
    session: Session,
    *,
    user_id: str,
    pending_email: str,
    raw_token: str,
    token_type: str = "registration",
    expires_in_hours: int = 24,
) -> EmailVerificationToken:
    """
    Invalidate previous unused verification tokens for user and create a new hashed token.
    """
    now = datetime.now(timezone.utc)
    session.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == user_id,
        EmailVerificationToken.used_at.is_(None),
    ).update({"used_at": now}, synchronize_session=False)

    token_record = EmailVerificationToken(
        user_id=user_id,
        pending_email=pending_email.strip().lower(),
        token_hash=hash_token(raw_token),
        token_type=token_type,
        expires_at=now + timedelta(hours=expires_in_hours),
        created_at=now,
    )
    session.add(token_record)
    session.commit()
    session.refresh(token_record)
    return token_record


def get_valid_email_verification_token(
    session: Session, raw_token: str
) -> EmailVerificationToken | None:
    """
    Retrieve token if it matches hash, has not been used, and has not expired.
    """
    token_hash = hash_token(raw_token)
    now = datetime.now(timezone.utc)
    return (
        session.query(EmailVerificationToken)
        .filter(
            EmailVerificationToken.token_hash == token_hash,
            EmailVerificationToken.used_at.is_(None),
            EmailVerificationToken.expires_at > now,
        )
        .first()
    )


def mark_email_verification_token_used(
    session: Session, token: EmailVerificationToken
) -> None:
    """Mark a verification token as consumed."""
    token.used_at = datetime.now(timezone.utc)
    session.add(token)
    session.commit()


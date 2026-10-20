from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.refresh_token import RefreshToken

logger = logging.getLogger("smart-farming.token")


def hash_token(token: str) -> str:
    """Computes a secure SHA-256 digest of a token string for database indexing."""
    return hashlib.sha256(token.strip().encode("utf-8")).hexdigest()


def store_refresh_token(
    session: Session,
    user_id: str,
    token_str: str,
    expires_delta: timedelta = timedelta(days=30),
) -> RefreshToken:
    """Stores a newly issued refresh token hash in the database."""
    token_h = hash_token(token_str)
    expires_at = datetime.now(timezone.utc) + expires_delta
    record = RefreshToken(
        user_id=user_id,
        token_hash=token_h,
        expires_at=expires_at,
        revoked=False,
    )
    session.add(record)
    session.flush()
    return record


def rotate_refresh_token(
    session: Session,
    old_token_str: str,
    new_token_str: str,
    new_expires_delta: timedelta = timedelta(days=30),
) -> Optional[RefreshToken]:
    """
    Performs refresh token rotation with reuse detection.
    If an already-revoked token is submitted, invalidates all sessions for the user.
    """
    old_hash = hash_token(old_token_str)
    record = session.query(RefreshToken).filter(RefreshToken.token_hash == old_hash).first()

    if not record:
        logger.warning("AUTH: Refresh attempt with unrecorded token hash.")
        return None

    # REUSE DETECTION: An already revoked token is being presented again
    if record.revoked:
        logger.critical(
            "SECURITY: Refresh token reuse detected for user %s! Invalidating all active user sessions.",
            record.user_id,
        )
        # Invalidate all refresh tokens for this user
        session.query(RefreshToken).filter(
            RefreshToken.user_id == record.user_id,
            RefreshToken.revoked == False,
        ).update({"revoked": True})
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compromised refresh token reuse detected. All active sessions have been terminated.",
        )

    # Check expiration
    now = datetime.now(timezone.utc)
    expires = record.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < now:
        record.revoked = True
        session.commit()
        return None

    # Rotate: mark old as revoked and record new token
    new_hash = hash_token(new_token_str)
    record.revoked = True
    record.replaced_by_hash = new_hash

    new_record = RefreshToken(
        user_id=record.user_id,
        token_hash=new_hash,
        expires_at=now + new_expires_delta,
        revoked=False,
    )
    session.add(new_record)
    session.commit()
    return new_record


def revoke_refresh_token(session: Session, token_str: str) -> bool:
    """Revokes a refresh token on logout."""
    token_h = hash_token(token_str)
    record = session.query(RefreshToken).filter(RefreshToken.token_hash == token_h).first()
    if record and not record.revoked:
        record.revoked = True
        session.commit()
        return True
    return False

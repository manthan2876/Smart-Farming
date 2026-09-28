from __future__ import annotations

import hashlib
import hmac
import logging
import time
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
import jwt
from sqlalchemy.orm import Session

from app.core import get_session
from app.core.config import settings

logger = logging.getLogger("smart-farming.internal_cron")
router = APIRouter(prefix="/internal/cron", tags=["Internal Cron"])


async def verify_qstash_signature(
    request: Request,
    upstash_signature: str | None = Header(default=None, alias="Upstash-Signature"),
    authorization: str | None = Header(default=None),
    x_cron_secret: str | None = Header(default=None, alias="X-Cron-Secret"),
) -> bool:
    """Verifies that an incoming request is legitimately from Upstash QStash or an authorized runner.

    Supports:
    1. Multi-region cryptographic Upstash-Signature JWT verification (checks EU & US signing keys).
    2. Shared CRON_SECRET bearer token or header for manual testing / admin triggers.
    """
    # 1. Check CRON_SECRET fallback (useful for local testing, staging, and manual curl)
    if settings.CRON_SECRET:
        secret = settings.CRON_SECRET.strip()
        if authorization and authorization.startswith("Bearer "):
            token = authorization[7:].strip()
            if hmac.compare_digest(token, secret):
                return True
        if x_cron_secret and hmac.compare_digest(x_cron_secret.strip(), secret):
            return True

    # 2. In local DEBUG mode with no keys configured, allow calls for development
    signing_keys = settings.all_qstash_signing_keys
    if not signing_keys:
        if settings.DEBUG:
            logger.warning("No QStash signing keys configured; allowing request in DEBUG mode.")
            return True
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="QStash signing keys are not configured on this server.",
        )

    # 3. Require Upstash-Signature header
    if not upstash_signature:
        logger.warning("Rejected cron invocation: Missing Upstash-Signature header.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Upstash-Signature header.",
        )

    # 4. Read body bytes for sha256 body integrity check
    body_bytes = await request.body()
    body_sha = hashlib.sha256(body_bytes).hexdigest() if body_bytes else None

    # 5. Verify JWT against configured QStash signing keys (multi-region support)
    verified = False
    last_error: str | None = None

    for key in signing_keys:
        try:
            payload = jwt.decode(
                upstash_signature,
                key,
                algorithms=["HS256"],
                options={"verify_exp": True, "verify_iss": False},
            )
            # If body claim is present in JWT, verify payload hash integrity
            expected_body_sha = payload.get("body")
            if expected_body_sha and body_sha and expected_body_sha != body_sha:
                last_error = "Body hash mismatch"
                continue

            verified = True
            break
        except jwt.ExpiredSignatureError:
            last_error = "Signature has expired"
        except jwt.InvalidSignatureError:
            last_error = "Invalid signature for key"
        except Exception as exc:
            last_error = str(exc)

    if not verified:
        logger.warning("Rejected cron invocation: QStash signature verification failed (%s)", last_error)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unauthorized: QStash signature verification failed ({last_error}).",
        )

    return True


@router.post("/weather-risks")
async def trigger_weather_risks(
    verified: bool = Depends(verify_qstash_signature),
) -> dict[str, Any]:
    """Triggered exclusively by Upstash QStash 3x/day (0 6,12,18 * * *).

    Evaluates microclimate disease risks across all plots and enqueues alerts.
    """
    logger.info("Executing QStash-scheduled weather risk evaluation...")
    from app.services.weather.proactive import evaluate_weather_risks

    try:
        await evaluate_weather_risks()
        return {
            "status": "success",
            "message": "Weather risks evaluated successfully.",
            "timestamp": time.time(),
        }
    except Exception as exc:
        logger.error("Weather risk evaluation failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Weather evaluation error: {exc}",
        )


@router.post("/purge-blobs")
async def trigger_purge_blobs(
    verified: bool = Depends(verify_qstash_signature),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Triggered exclusively by Upstash QStash weekly on Sunday (0 3 * * 0).

    Purges unreferenced images and audio files older than 1 hour.
    """
    logger.info("Executing QStash-scheduled orphaned blob purge...")
    from app.core.storage import purge_orphaned_blobs

    try:
        res = purge_orphaned_blobs(session, dry_run=False, grace_seconds=3600)
        return {
            "status": "success",
            "message": "Orphaned blob purge completed.",
            "result": res,
            "timestamp": time.time(),
        }
    except Exception as exc:
        logger.error("Orphaned blob purge failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blob purge error: {exc}",
        )

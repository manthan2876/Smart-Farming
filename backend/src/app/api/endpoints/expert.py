from __future__ import annotations

import logging
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import require_expert_role
from app.core import get_session
from app.schemas.expert import (
    ExpertQueueItemResponse,
    ExpertReviewDetailResponse,
    ExpertReviewSubmissionRequest,
    ExpertReviewSubmissionResponse,
)
from app.services.expert import (
    get_queue_items,
    get_review_detail,
    claim_review_lease,
    release_review_lease,
    submit_review_decision,
)

logger = logging.getLogger("smart-farming.api.expert")
router = APIRouter(tags=["expert"])


@router.get("/expert/queue", response_model=list[ExpertQueueItemResponse])
def get_expert_queue(
    session: Session = Depends(get_session),
    user_id: str = Depends(require_expert_role),
) -> list[dict[str, Any]]:
    """Retrieve pending scans escalated for human agronomist review."""
    try:
        return get_queue_items(session)
    except SQLAlchemyError as exc:
        logger.exception("Database error while loading expert queue")
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc


@router.get(
    "/expert/reviews/{review_id}",
    response_model=ExpertReviewDetailResponse,
)
def get_expert_review(
    request: Request,
    review_id: int,
    lang: str | None = None,
    session: Session = Depends(get_session),
    user_id: str = Depends(require_expert_role),
) -> dict[str, Any]:
    """Retrieve detailed metadata, imagery, and advisory info for a specific scan review."""
    try:
        accept_lang = request.headers.get("accept-language")
        return get_review_detail(session, review_id, lang=lang, accept_language=accept_lang)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.exception("Database error while loading review %s", review_id)
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc


@router.post("/expert/reviews/{review_id}/claim")
def claim_expert_review(
    review_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(require_expert_role),
) -> dict[str, Any]:
    """Atomically claims a review item for 15 minutes to prevent expert collisions."""
    try:
        return claim_review_lease(session, review_id, user_id)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        session.rollback()
        logger.exception("Database error claiming review %s", review_id)
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc


@router.post("/expert/reviews/{review_id}/release")
def release_expert_review(
    review_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(require_expert_role),
) -> dict[str, Any]:
    """Releases a claimed review item back to the shared queue."""
    try:
        return release_review_lease(session, review_id, user_id)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        session.rollback()
        logger.exception("Database error releasing review %s", review_id)
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc


@router.post(
    "/expert/reviews/{review_id}",
    response_model=ExpertReviewSubmissionResponse,
)
async def post_expert_review(
    review_id: int,
    payload: ExpertReviewSubmissionRequest,
    session: Session = Depends(get_session),
    user_id: str = Depends(require_expert_role),
) -> dict[str, Any]:
    """Submit an expert diagnostic decision, alert the farmer, and optionally flag for model retraining."""
    try:
        result, new_alert, farmer_guidance = submit_review_decision(
            session=session,
            review_id=review_id,
            user_id=user_id,
            payload=payload,
        )

        # Enqueue background transliteration/translations asynchronously
        from app.core.arq import enqueue_translation
        if farmer_guidance:
            try:
                await enqueue_translation("expert_review", review_id, {"farmer_guidance": farmer_guidance})
            except Exception:
                # Background transliteration failure must not fail review submission
                pass
        if new_alert and new_alert.id:
            try:
                await enqueue_translation("alert", new_alert.id, {"title": new_alert.title, "body": new_alert.body})
            except Exception:
                # Background transliteration failure must not fail review submission
                pass

        return result
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        session.rollback()
        logger.exception("Database error submitting review %s", review_id)
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc

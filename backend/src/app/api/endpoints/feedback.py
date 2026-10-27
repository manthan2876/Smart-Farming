from __future__ import annotations

import logging
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_expert_role
from app.core import get_session
from app.schemas import FeedbackRequest, FeedbackResponse, FeedbackReviewRequest
from app.schemas.admin import FeedbackReviewResponse
from app.services.feedback import (
    create_farmer_feedback,
    update_farmer_feedback as update_feedback_service,
    review_farmer_feedback as review_feedback_service,
)

logger = logging.getLogger("smart-farming.api.feedback")
router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse, status_code=201)
def feedback(
    payload: FeedbackRequest,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> FeedbackResponse:
    """Submit farmer feedback on a diagnostic prediction."""
    try:
        saved = create_farmer_feedback(session, user_id, payload)
        return FeedbackResponse(
            id=saved.id,
            prediction_id=saved.prediction_id,
            is_correct=saved.is_correct,
            farmer_note=saved.farmer_note,
        )
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        session.rollback()
        safe_uid = str(user_id).replace("\r", "").replace("\n", "")
        logger.exception("Database error while submitting feedback for user %s", safe_uid)
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc


@router.put("/feedback/{feedback_id}", response_model=FeedbackResponse)
def update_feedback(
    feedback_id: int,
    payload: FeedbackRequest,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> FeedbackResponse:
    """Update an existing farmer feedback submission."""
    try:
        fb = update_feedback_service(session, user_id, feedback_id, payload)
        return FeedbackResponse(
            id=fb.id,
            prediction_id=fb.prediction_id,
            is_correct=fb.is_correct,
            farmer_note=fb.farmer_note,
        )
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        session.rollback()
        safe_fbid = str(feedback_id).replace("\r", "").replace("\n", "")
        logger.exception("Database error updating feedback %s", safe_fbid)
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc


@router.post(
    "/feedback/{feedback_id}/review",
    status_code=200,
    response_model=FeedbackReviewResponse,
)
def review_feedback(
    feedback_id: int,
    payload: FeedbackReviewRequest,
    user_id: str = Depends(require_expert_role),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Expert adjudication on farmer feedback with optional diagnosis correction."""
    try:
        return review_feedback_service(session, user_id, feedback_id, payload)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        session.rollback()
        safe_fbid = str(feedback_id).replace("\r", "").replace("\n", "")
        logger.exception("Database error reviewing feedback %s", safe_fbid)
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc

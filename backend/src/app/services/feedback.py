from __future__ import annotations

import logging
from typing import Any
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.crud.feedback import (
    get_feedback_by_id,
    add_feedback,
    update_feedback_content,
    apply_feedback_review,
)
from app.models import Feedback, Prediction
from app.schemas import FeedbackRequest, FeedbackReviewRequest
from app.utils import prediction_event

logger = logging.getLogger("smart-farming.services.feedback")


def create_farmer_feedback(
    session: Session,
    user_id: str,
    payload: FeedbackRequest,
) -> Feedback:
    """Validate ownership, record feedback, and emit telemetry event."""
    prediction = session.get(Prediction, payload.prediction_id)
    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found.")
    if str(prediction.user_id) != str(user_id):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: You can only submit feedback for your own predictions.",
        )

    try:
        saved = add_feedback(
            session=session,
            prediction=prediction,
            is_correct=payload.is_correct,
            farmer_note=payload.farmer_note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    safe_user_id = str(user_id).replace("\r", "").replace("\n", "")
    prediction_event(
        logger,
        "feedback_recorded",
        prediction_id=saved.prediction_id,
        user_id=safe_user_id,
        is_correct=saved.is_correct,
    )
    return saved


def update_farmer_feedback(
    session: Session,
    user_id: str,
    feedback_id: int,
    payload: FeedbackRequest,
) -> Feedback:
    """Validate ownership and update farmer feedback submission."""
    fb = get_feedback_by_id(session, feedback_id)
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found.")

    prediction = fb.prediction
    if not prediction or str(prediction.user_id) != str(user_id):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: You can only update feedback on your own predictions.",
        )

    return update_feedback_content(
        session=session,
        feedback=fb,
        is_correct=payload.is_correct,
        farmer_note=payload.farmer_note,
    )


def review_farmer_feedback(
    session: Session,
    reviewer_id: str,
    feedback_id: int,
    payload: FeedbackReviewRequest,
) -> dict[str, Any]:
    """Expert review and adjudication of farmer feedback."""
    fb = get_feedback_by_id(session, feedback_id)
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found")

    updated = apply_feedback_review(
        session=session,
        feedback=fb,
        reviewer_id=reviewer_id,
        status=payload.status,
        reviewer_note=payload.reviewer_note,
        corrected_label=payload.corrected_label,
    )

    return {
        "status": "success",
        "feedback_id": updated.id,
        "review_status": updated.review_status,
        "corrected_label": updated.corrected_label,
    }

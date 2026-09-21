from __future__ import annotations

import logging

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.schemas import FeedbackRequest, FeedbackResponse, FeedbackReviewRequest
from app.api.deps import get_current_user, require_expert_role
from app.core import get_session
from app.crud import get_prediction, add_feedback
from app.utils import prediction_event
from app.models import Feedback, DatasetCandidate

router = APIRouter()

_LOGGER = logging.getLogger("smart-farming.api")

@router.post("/feedback", response_model=FeedbackResponse, status_code=201)
async def feedback(
    payload: FeedbackRequest,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> FeedbackResponse:
    try:
        prediction = get_prediction(session, payload.prediction_id, user_id)
        if prediction is None:
            raise HTTPException(status_code=404, detail="Prediction not found.")
        try:
            saved = add_feedback(session, prediction, payload.is_correct, payload.farmer_note)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        prediction_event(
            _LOGGER,
            "feedback_recorded",
            prediction_id=saved.prediction_id,
            user_id=user_id,
            is_correct=saved.is_correct,
        )
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    return FeedbackResponse(
        id=saved.id,
        prediction_id=saved.prediction_id,
        is_correct=saved.is_correct,
        farmer_note=saved.farmer_note,
    )


@router.post("/feedback/{feedback_id}/review", status_code=200)
async def review_feedback(
    feedback_id: int,
    payload: FeedbackReviewRequest,
    user_id: str = Depends(require_expert_role),
    session: Session = Depends(get_session),
) -> dict:
    feedback = session.get(Feedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    feedback.review_status = payload.status
    feedback.review_decision = payload.status
    feedback.reviewer_id = user_id
    feedback.reviewer_note = payload.reviewer_note
    feedback.reviewed_at = datetime.now(timezone.utc)

    if payload.status == "approved" and not feedback.is_correct:
        prediction = feedback.prediction
        existing_candidate = session.scalar(
            select(DatasetCandidate).where(DatasetCandidate.prediction_id == prediction.id)
        )
        if existing_candidate is None:
            session.add(DatasetCandidate(
                prediction_id=prediction.id,
                source="farmer_feedback_review",
                original_label=prediction.disease,
                corrected_label=payload.corrected_label,
                image_path=prediction.image.raw_path if prediction.image else prediction.raw_path,
                status="pending_review",
            ))

    session.commit()
    
    return {"status": "success", "feedback_id": feedback.id, "review_status": feedback.review_status}

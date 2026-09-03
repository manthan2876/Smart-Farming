from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas import FeedbackRequest, FeedbackResponse
from app.api.deps import get_current_user, require_expert_role
from app.core import get_session
from app.crud import get_prediction, add_feedback
from app.utils import prediction_event

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
        saved = add_feedback(
            session, prediction, payload.is_correct, payload.farmer_note
        )
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
    payload: dict,
    user_id: str = Depends(require_expert_role),
    session: Session = Depends(get_session),
) -> dict:
    feedback = session.query(Feedback).get(feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    # Example handling: just acknowledging the review in this prototype
    # Could store 'status' or 'expert_status' on the Feedback model if needed.
    
    return {"status": "success"}

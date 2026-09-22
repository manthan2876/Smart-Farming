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
        from app.models import Prediction
        prediction = session.get(Prediction, payload.prediction_id)
        if prediction is None:
            raise HTTPException(status_code=404, detail="Prediction not found.")
        if str(prediction.user_id) != str(user_id):
            raise HTTPException(status_code=403, detail="Forbidden: You can only submit feedback for your own predictions.")
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


@router.put("/feedback/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
    feedback_id: int,
    payload: FeedbackRequest,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> FeedbackResponse:
    """Update an existing farmer feedback submission."""
    fb = session.get(Feedback, feedback_id)
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found.")
    prediction = fb.prediction
    if not prediction or str(prediction.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail="Forbidden: You can only update feedback on your own predictions.")

    fb.is_correct = payload.is_correct
    fb.farmer_note = payload.farmer_note
    session.add(fb)
    session.commit()
    return FeedbackResponse(
        id=fb.id,
        prediction_id=fb.prediction_id,
        is_correct=fb.is_correct,
        farmer_note=fb.farmer_note,
    )


@router.post("/feedback/{feedback_id}/review", status_code=200)
async def review_feedback(
    feedback_id: int,
    payload: FeedbackReviewRequest,
    user_id: str = Depends(require_expert_role),
    session: Session = Depends(get_session),
) -> dict:
    from sqlalchemy.orm.attributes import flag_modified
    fb = session.get(Feedback, feedback_id)
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found")

    # Persist all review fields including corrected label
    fb.review_status = payload.status
    fb.review_decision = payload.status
    fb.reviewer_id = user_id
    fb.reviewer_note = payload.reviewer_note
    fb.corrected_label = payload.corrected_label
    fb.reviewed_at = datetime.now(timezone.utc)

    if payload.status == "approved":
        prediction = fb.prediction
        if prediction and payload.corrected_label:
            # Merge corrected diagnosis back into prediction record and public result
            prediction.disease = payload.corrected_label
            if isinstance(prediction.result, dict):
                res = dict(prediction.result)
                if "disease" in res and isinstance(res["disease"], dict):
                    res["disease"]["label"] = payload.corrected_label
                    res["disease"]["is_corrected"] = True
                prediction.result = res
                flag_modified(prediction, "result")

        if not fb.is_correct and prediction:
            orig_disease = (
                prediction.result.get("disease", {}).get("label") if prediction.result else None
            ) or prediction.disease
            corrected = payload.corrected_label or orig_disease
            image_path = prediction.image.raw_path if prediction.image else prediction.raw_path or ""

            existing_candidate = session.scalar(
                select(DatasetCandidate).where(DatasetCandidate.prediction_id == prediction.id)
            )
            if existing_candidate is None:
                provenance = (
                    f"Farmer marked incorrect. "
                    f"Reviewer ({user_id}) approved correction on feedback #{feedback_id}."
                    + (f" Corrected label: {corrected}." if corrected != orig_disease else "")
                )
                session.add(DatasetCandidate(
                    prediction_id=prediction.id,
                    source="farmer_feedback_review",
                    original_label=orig_disease,
                    corrected_label=corrected,
                    image_path=image_path,
                    status="pending_review",
                    provenance_note=provenance,
                    source_feedback_id=feedback_id,
                ))
            else:
                if payload.corrected_label and existing_candidate.corrected_label != payload.corrected_label:
                    existing_candidate.corrected_label = payload.corrected_label
                    existing_candidate.provenance_note = (
                        (existing_candidate.provenance_note or "") +
                        f" | Reviewer {user_id} updated correction to: {payload.corrected_label}."
                    )

    session.commit()

    return {
        "status": "success",
        "feedback_id": fb.id,
        "review_status": fb.review_status,
        "corrected_label": fb.corrected_label,
    }



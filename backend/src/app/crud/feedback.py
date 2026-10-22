from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified
from app.models import (
    Feedback,
    Prediction,
    DatasetCandidate,
)


def get_feedback_by_id(session: Session, feedback_id: int) -> Feedback | None:
    """Retrieve a feedback entry by ID."""
    return session.get(Feedback, feedback_id)


def add_feedback(
    session: Session,
    prediction: Prediction,
    is_correct: bool,
    farmer_note: str | None,
) -> Feedback:
    """Insert a new farmer feedback entry and optionally flag as dataset candidate."""
    existing_feedback = session.scalar(
        select(Feedback).where(Feedback.prediction_id == prediction.id)
    )
    if existing_feedback is not None:
        raise ValueError("Feedback has already been submitted for this prediction")

    feedback = Feedback(
        prediction_id=prediction.id,
        is_correct=is_correct,
        farmer_note=farmer_note,
    )
    session.add(feedback)

    # If the farmer confirms the prediction is correct, add it to DatasetCandidate for MLOps
    if is_correct:
        try:
            existing = session.query(DatasetCandidate).filter(
                DatasetCandidate.prediction_id == prediction.id
            ).first()
            if not existing:
                candidate = DatasetCandidate(
                    prediction_id=prediction.id,
                    source="farmer_confirmation",
                    original_label=prediction.disease,
                    corrected_label=prediction.disease,
                    image_path=prediction.image.raw_path if prediction.image else "",
                )
                session.add(candidate)
        except Exception:
            pass

    session.commit()
    session.refresh(feedback)
    return feedback


def update_feedback_content(
    session: Session,
    feedback: Feedback,
    is_correct: bool,
    farmer_note: str | None,
) -> Feedback:
    """Update fields on an existing farmer feedback."""
    feedback.is_correct = is_correct
    feedback.farmer_note = farmer_note
    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    return feedback


def apply_feedback_review(
    session: Session,
    feedback: Feedback,
    reviewer_id: str,
    status: str,
    reviewer_note: str | None,
    corrected_label: str | None,
) -> Feedback:
    """Apply an expert review to farmer feedback and update dataset candidates accordingly."""
    feedback.review_status = status
    feedback.review_decision = status
    feedback.reviewer_id = reviewer_id
    feedback.reviewer_note = reviewer_note
    feedback.corrected_label = corrected_label
    feedback.reviewed_at = datetime.now(timezone.utc)

    if status == "approved":
        prediction = feedback.prediction
        if prediction and corrected_label:
            prediction.disease = corrected_label
            if isinstance(prediction.result, dict):
                res = dict(prediction.result)
                if "disease" in res and isinstance(res["disease"], dict):
                    res["disease"]["label"] = corrected_label
                    res["disease"]["is_corrected"] = True
                prediction.result = res
                flag_modified(prediction, "result")

        if not feedback.is_correct and prediction:
            orig_disease = (
                prediction.result.get("disease", {}).get("label") if prediction.result else None
            ) or prediction.disease
            corrected = corrected_label or orig_disease
            image_path = prediction.image.raw_path if prediction.image else prediction.raw_path or ""

            existing_candidate = session.scalar(
                select(DatasetCandidate).where(DatasetCandidate.prediction_id == prediction.id)
            )
            if existing_candidate is None:
                provenance = (
                    f"Farmer marked incorrect. "
                    f"Reviewer ({reviewer_id}) approved correction on feedback #{feedback.id}."
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
                    source_feedback_id=feedback.id,
                ))
            else:
                if corrected_label and existing_candidate.corrected_label != corrected_label:
                    existing_candidate.corrected_label = corrected_label
                    existing_candidate.provenance_note = (
                        (existing_candidate.provenance_note or "")
                        + f" | Reviewer {reviewer_id} updated correction to: {corrected_label}."
                    )

    session.commit()
    session.refresh(feedback)
    return feedback

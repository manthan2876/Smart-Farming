from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import (
    Feedback,
    Prediction,
    DatasetCandidate,
)

def add_feedback(
    session: Session,
    prediction: Prediction,
    is_correct: bool,
    farmer_note: str | None,
) -> Feedback:
    feedback = Feedback(
        prediction_id=prediction.id,
        is_correct=is_correct,
        farmer_note=farmer_note,
    )
    session.add(feedback)
    
    # If the farmer confirms the prediction is correct, add it to DatasetCandidate for MLOps
    if is_correct:
        try:
            # Check if it already exists to avoid unique constraint violations on prediction_id
            existing = session.query(DatasetCandidate).filter(DatasetCandidate.prediction_id == prediction.id).first()
            if not existing:
                candidate = DatasetCandidate(
                    prediction_id=prediction.id,
                    source="farmer_confirmation",
                    original_label=prediction.disease,
                    corrected_label=prediction.disease,
                    image_path=prediction.image.raw_path if prediction.image else ""
                )
                session.add(candidate)
        except Exception:
            pass # Ignore if error

    session.commit()
    session.refresh(feedback)
    return feedback

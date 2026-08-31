from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import (
    Feedback,
    Prediction,
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
    session.commit()
    session.refresh(feedback)
    return feedback

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import ExpertReview, Prediction


def ensure_expert_review(
    session: Session,
    prediction: Prediction,
    reason: str,
) -> ExpertReview:
    review = prediction.expert_review
    if review is None:
        review = ExpertReview(
            prediction_id=prediction.id,
            status="pending",
            internal_note=reason,
        )
        session.add(review)
    elif review.status in {"verified", "rejected"}:
        return review
    else:
        review.status = "pending"
        review.internal_note = reason

    prediction.status = "pending_expert_review"
    result = dict(prediction.result or {})
    result_status = dict(result.get("status") or {})
    result_status["expert_review"] = "pending"
    result["status"] = result_status
    prediction.result = result
    return review

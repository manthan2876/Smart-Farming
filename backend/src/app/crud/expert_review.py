from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import select
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


def get_pending_reviews(session: Session) -> list[ExpertReview]:
    """Retrieve all pending expert reviews ordered by creation date descending."""
    return list(
        session.scalars(
            select(ExpertReview)
            .where(ExpertReview.status == "pending")
            .order_by(ExpertReview.created_at.desc())
        )
    )


def get_review_by_id(session: Session, review_id: int) -> ExpertReview | None:
    """Retrieve a single expert review by its ID."""
    return session.get(ExpertReview, review_id)


def claim_review(session: Session, review: ExpertReview, expert_id: str) -> None:
    """Assign an expert claim with current UTC timestamp."""
    review.claimed_by = expert_id
    review.claimed_at = datetime.now(timezone.utc)
    session.add(review)
    session.commit()


def release_review(session: Session, review: ExpertReview) -> None:
    """Clear claim on a review item and return it to the queue."""
    review.claimed_by = None
    review.claimed_at = None
    session.add(review)
    session.commit()

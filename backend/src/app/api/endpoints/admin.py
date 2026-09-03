from __future__ import annotations
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import sqlalchemy as sa
from app.models import DatasetCandidate, Farm, Image, Recommendation, Alert, Plot, ExpertReview
from app.api.deps import require_admin_role, require_expert_role
from app.core import get_session
from app.models import Prediction, Feedback, User

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/metrics")
async def get_metrics(
    user_id: str = Depends(require_admin_role), session: Session = Depends(get_session)
) -> dict[str, Any]:
    total_users = session.query(func.count(User.id)).scalar()
    total_scans = session.query(func.count(Prediction.id)).scalar()
    
    # Accuracy trend (simplification: total feedback)
    correct_count = session.query(func.count(Feedback.id)).filter(Feedback.is_correct == True).scalar()
    total_feedback = session.query(func.count(Feedback.id)).scalar()
    accuracy = (correct_count / total_feedback * 100) if total_feedback else 100.0

    # Disease distribution
    diseases = session.query(Prediction.disease, func.count(Prediction.id)).group_by(Prediction.disease).all()
    disease_dist = [{"name": d[0] or "Unknown", "value": d[1]} for d in diseases if d[0]]

    # Confidence brackets
    high_conf = session.query(func.count(Prediction.id)).filter(Prediction.disease_conf >= 0.75).scalar()
    med_conf = session.query(func.count(Prediction.id)).filter(Prediction.disease_conf >= 0.50, Prediction.disease_conf < 0.75).scalar()
    low_conf = session.query(func.count(Prediction.id)).filter(Prediction.disease_conf < 0.50).scalar()

    return {
        "total_users": total_users,
        "total_scans": total_scans,
        "accuracy": accuracy,
        "disease_distribution": disease_dist,
        "confidence_histogram": [
            {"name": "High (>75%)", "count": high_conf},
            {"name": "Medium (50-75%)", "count": med_conf},
            {"name": "Low (<50%)", "count": low_conf},
        ]
    }


@router.delete("/purge")
async def purge_database(
    user_id: str = Depends(require_admin_role), session: Session = Depends(get_session)
) -> dict[str, Any]:
    session.execute(sa.delete(DatasetCandidate))
    session.execute(sa.delete(ExpertReview))
    session.execute(sa.delete(Recommendation))
    session.execute(sa.delete(Feedback))
    session.execute(sa.delete(Alert))
    # Prediction has parent_id, so we can delete all
    session.execute(sa.delete(Prediction))
    session.execute(sa.delete(Image))
    session.execute(sa.delete(Plot))
    session.execute(sa.delete(Farm))
    
    # Delete all non-admin users, or just non-current users
    session.execute(sa.delete(User).where(User.id != user_id))
    
    session.commit()
    return {"status": "success", "message": "Database wiped successfully."}


@router.get("/feedback")
async def get_feedback(
    user_id: str = Depends(require_expert_role), session: Session = Depends(get_session)
) -> list[dict[str, Any]]:
    feedbacks = session.query(Feedback).order_by(Feedback.created_at.desc()).all()
    results = []
    for f in feedbacks:
        pred = f.prediction
        results.append({
            "id": f.id,
            "prediction_id": f.prediction_id,
            "crop": pred.crop if pred else None,
            "disease": pred.disease if pred else None,
            "is_correct": f.is_correct,
            "farmer_note": f.farmer_note,
            "created_at": str(f.created_at)
        })
    return results

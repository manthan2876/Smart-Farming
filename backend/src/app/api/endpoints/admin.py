from __future__ import annotations
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import require_admin_role
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

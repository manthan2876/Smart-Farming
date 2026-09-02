from __future__ import annotations
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core import get_session
from app.models import Prediction, Feedback, Image, User

router = APIRouter(tags=["admin"])

@router.get("/admin/metrics")
async def get_admin_metrics(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user),
) -> dict[str, Any]:
    total_predictions = session.scalar(select(func.count(Prediction.id))) or 0
    total_feedback = session.scalar(select(func.count(Feedback.id))) or 0
    correct_feedback = session.scalar(
        select(func.count(Feedback.id)).where(Feedback.is_correct == True)
    ) or 0
    accuracy_rate = (
        round((correct_feedback / total_feedback) * 100, 2)
        if total_feedback > 0
        else 100.0
    )
    avg_crop_conf = session.scalar(select(func.avg(Prediction.crop_conf))) or 0.0
    avg_disease_conf = session.scalar(select(func.avg(Prediction.disease_conf))) or 0.0
    avg_quality = session.scalar(select(func.avg(Image.quality_score))) or 0.0

    crop_counts_query = (
        select(Prediction.crop, func.count(Prediction.id))
        .where(Prediction.crop != None)
        .group_by(Prediction.crop)
    )
    crop_distribution = {
        crop: count for crop, count in session.execute(crop_counts_query).all()
    }

    disease_counts_query = (
        select(Prediction.disease, func.count(Prediction.id))
        .where(Prediction.disease != None)
        .group_by(Prediction.disease)
    )
    disease_distribution = {
        disease: count for disease, count in session.execute(disease_counts_query).all()
    }

    return {
        "total_predictions": total_predictions,
        "total_feedback": total_feedback,
        "accuracy_rate_pct": accuracy_rate,
        "avg_crop_confidence": round(float(avg_crop_conf), 4),
        "avg_disease_confidence": round(float(avg_disease_conf), 4),
        "avg_image_quality_score": round(float(avg_quality), 2),
        "crop_distribution": crop_distribution,
        "disease_distribution": disease_distribution,
        "status": "healthy",
    }


@router.get("/admin/feedback")
async def get_admin_feedback(
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user),
) -> list[dict[str, Any]]:
    feedback_list = list(
        session.scalars(
            select(Feedback)
            .order_by(Feedback.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
    )
    return [
        {
            "id": item.id,
            "prediction_id": item.prediction_id,
            "is_correct": item.is_correct,
            "farmer_note": item.farmer_note,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
        for item in feedback_list
    ]

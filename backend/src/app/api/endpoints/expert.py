from __future__ import annotations
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core import get_session
from app.models import Prediction, ExpertReview

router = APIRouter(tags=["expert"])

@router.get("/expert/queue")
async def get_expert_queue(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user),
):
    reviews = list(
        session.scalars(
            select(ExpertReview)
            .where(ExpertReview.status == "pending")
            .order_by(ExpertReview.created_at.desc())
        )
    )
    results = []
    for r in reviews:
        pred = r.prediction
        results.append({
            "review_id": r.id,
            "prediction_id": r.prediction_id,
            "status": r.status,
            "crop": pred.crop,
            "disease": pred.disease,
            "disease_conf": pred.disease_conf,
            "severity_pct": pred.severity_pct,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
    return results

@router.get("/expert/reviews/{review_id}")
async def get_expert_review(
    review_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user),
):
    review = session.get(ExpertReview, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    pred = review.prediction
    return {
        "review_id": review.id,
        "prediction_id": review.prediction_id,
        "status": review.status,
        "decision": review.decision,
        "corrected_disease": review.corrected_disease,
        "farmer_guidance": review.farmer_guidance,
        "internal_note": review.internal_note,
        "raw_path": pred.raw_path,
        "processed_path": pred.processed_path,
        "crop": pred.crop,
        "disease": pred.disease,
        "disease_conf": pred.disease_conf,
        "severity_pct": pred.severity_pct,
        "created_at": review.created_at.isoformat() if review.created_at else None
    }

from sqlalchemy.orm.attributes import flag_modified

@router.post("/expert/reviews/{review_id}")
async def post_expert_review(
    review_id: int,
    payload: dict,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user),
):
    review = session.get(ExpertReview, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
        
    action = payload.get("action")
    review.decision = action
    review.status = "verified"
    review.expert_id = user_id
    
    if action == "Correct Diagnosis":
        review.corrected_disease = payload.get("corrected_disease")
        
    review.farmer_guidance = payload.get("farmer_guidance")
    review.internal_note = payload.get("internal_note")
    
    # Update prediction status
    review.prediction.status = "verified"
    
    res = dict(review.prediction.result)
    if "status" in res and isinstance(res["status"], dict):
        # We need a new dictionary to trigger the change, or use flag_modified
        new_status = dict(res["status"])
        new_status["expert_review"] = "verified"
        res["status"] = new_status
        
    review.prediction.result = res
    flag_modified(review.prediction, "result")
    
    session.commit()
    return {"status": "success", "review_id": review_id}

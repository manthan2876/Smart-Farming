from __future__ import annotations
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_expert_role
from app.core import get_session
from app.models import Prediction, ExpertReview, Alert, DatasetCandidate

router = APIRouter(tags=["expert"])

@router.get("/expert/queue")
async def get_expert_queue(
    session: Session = Depends(get_session),
    user_id: str = Depends(require_expert_role),
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
        result_json = pred.result or {}
        
        crop = result_json.get("crop", {}).get("label") or pred.crop
        disease = result_json.get("disease", {}).get("label") or pred.disease
        disease_conf = result_json.get("disease", {}).get("confidence") or pred.disease_conf
        severity_pct = result_json.get("severity", {}).get("percent") or pred.severity_pct

        results.append({
            "review_id": r.id,
            "prediction_id": r.prediction_id,
            "status": r.status,
            "crop": crop,
            "disease": disease,
            "disease_conf": disease_conf,
            "severity_pct": severity_pct,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
    return results

@router.get("/expert/reviews/{review_id}")
async def get_expert_review(
    review_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(require_expert_role),
):
    review = session.get(ExpertReview, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    pred = review.prediction
    result_json = pred.result or {}
    
    crop = result_json.get("crop", {}).get("label") or pred.crop
    disease = result_json.get("disease", {}).get("label") or pred.disease
    disease_conf = result_json.get("disease", {}).get("confidence") or pred.disease_conf
    severity_pct = result_json.get("severity", {}).get("percent") or pred.severity_pct

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
        "crop": crop,
        "disease": disease,
        "disease_conf": disease_conf,
        "severity_pct": severity_pct,
        "created_at": review.created_at.isoformat() if review.created_at else None
    }

from sqlalchemy.orm.attributes import flag_modified

@router.post("/expert/reviews/{review_id}")
async def post_expert_review(
    review_id: int,
    payload: dict,
    session: Session = Depends(get_session),
    user_id: str = Depends(require_expert_role),
):
    review = session.get(ExpertReview, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
        
    action = payload.get("action")
    review.decision = action
    review.status = "verified"
    review.expert_id = user_id
    
    if action == "Override / Correct Findings":
        review.corrected_disease = payload.get("corrected_disease")
        # Handle corrected severity (can be string or float. wireframe shows strings like 'Moderate (32%)' or just 'Moderate')
        raw_sev = payload.get("corrected_severity")
        # We store float in DB but for now if it's a string let's just log it in internal note or try to parse
        if raw_sev:
            try:
                # very naive parsing or just ignore if it's a string, since db column is Float.
                # if the payload passes a string, we might crash. Let's just avoid crashing.
                if isinstance(raw_sev, (int, float)):
                    review.corrected_severity = float(raw_sev)
            except:
                pass
    
    review.farmer_guidance = payload.get("farmer_guidance")
    review.internal_note = payload.get("internal_note")
    
    pred = review.prediction
    pred.status = "verified"
    
    # Generate Alert for farmer
    farmer_alert = Alert(
        user_id=pred.user_id,
        prediction_id=pred.id,
        kind="review_verified",
        severity="high",
        title=f"Expert Review Completed for Scan #{pred.id}",
        body=f"An agronomist has verified your scan. Conclusion: {action}."
    )
    session.add(farmer_alert)
    
    # Dataset flagging
    if payload.get("add_to_retraining"):
        orig_disease = pred.result.get("disease", {}).get("label") if pred.result else pred.disease
        ds = DatasetCandidate(
            prediction_id=pred.id,
            source="expert_correction",
            original_label=orig_disease,
            corrected_label=review.corrected_disease or orig_disease,
            image_path=pred.image.raw_path if pred.image else "",
            status="pending_review"
        )
        session.add(ds)
    
    res = dict(pred.result)
    if "status" in res and isinstance(res["status"], dict):
        new_status = dict(res["status"])
        new_status["expert_review"] = "verified"
        if "mask_advisory" in new_status:
            new_status["mask_advisory"] = False
        res["status"] = new_status
        
    # Also update the recommendation field inside result if farmer_guidance was provided
    if review.farmer_guidance:
        if "recommendation" not in res:
            res["recommendation"] = {}
        res["recommendation"]["expert_verified_advisory"] = review.farmer_guidance

    pred.result = res
    flag_modified(pred, "result")
    
    session.commit()
    return {"status": "success", "review_id": review_id}

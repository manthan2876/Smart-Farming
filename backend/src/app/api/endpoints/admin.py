from __future__ import annotations
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import sqlalchemy as sa
from app.models import DatasetCandidate, Farm, Image, Recommendation, Alert, Plot, ExpertReview
from app.api.deps import require_admin_role, require_expert_role
from app.core import get_session
from app.models import Prediction, Feedback, User
from app.core.config import settings
from app.core.paths import ensure_storage_directories, storage_relative_path

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/metrics")
async def get_metrics(
    user_id: str = Depends(require_admin_role), session: Session = Depends(get_session)
) -> dict[str, Any]:
    total_users = session.query(func.count(User.id)).scalar() or 0
    total_scans = session.query(func.count(Prediction.id)).scalar() or 0
    
    # Feedback accuracy
    correct_count = session.query(func.count(Feedback.id)).filter(Feedback.is_correct == True).scalar() or 0
    total_feedback = session.query(func.count(Feedback.id)).scalar() or 0
    accuracy = round((correct_count / total_feedback * 100), 1) if total_feedback else 100.0

    # Failures and processing status
    total_failed = session.query(func.count(Prediction.id)).filter(Prediction.status == "failed").scalar() or 0
    total_processing = session.query(func.count(Prediction.id)).filter(Prediction.status == "processing").scalar() or 0
    total_completed = session.query(func.count(Prediction.id)).filter(Prediction.status.in_(["ready", "completed", "verified", "pending_expert_review"])).scalar() or 0
    failure_rate = round((total_failed / total_scans * 100), 1) if total_scans else 0.0

    # Expert validation & corrections
    expert_total = session.query(func.count(ExpertReview.id)).scalar() or 0
    expert_overrides = session.query(func.count(ExpertReview.id)).filter(ExpertReview.decision == "override").scalar() or 0
    expert_approved = session.query(func.count(ExpertReview.id)).filter(ExpertReview.decision == "approve").scalar() or 0
    expert_pending = session.query(func.count(ExpertReview.id)).filter(ExpertReview.status == "pending").scalar() or 0
    decided_reviews = expert_approved + expert_overrides
    expert_validated_accuracy = round((expert_approved / decided_reviews * 100), 1) if decided_reviews > 0 else None

    # Processing durations & fallbacks
    predictions = session.query(Prediction.result, Prediction.status).all()
    durations: list[int] = []
    rec_fallbacks = 0
    weather_fallbacks = 0

    for res, st in predictions:
        if isinstance(res, dict):
            dur = res.get("total_duration_ms") or res.get("provenance", {}).get("pipeline_duration_ms")
            if dur is not None and isinstance(dur, (int, float)):
                durations.append(int(dur))
            elif "stages" in res and isinstance(res["stages"], dict):
                p_dur = res["stages"].get("pipeline", {}).get("duration_ms")
                if p_dur is not None and isinstance(p_dur, (int, float)):
                    durations.append(int(p_dur))
            if res.get("recommendation", {}).get("is_fallback") is True:
                rec_fallbacks += 1
            if res.get("weather", {}).get("is_degraded") is True:
                weather_fallbacks += 1

    durations.sort()
    avg_duration_ms = round(sum(durations) / len(durations)) if durations else 0
    p95_duration_ms = durations[int(len(durations) * 0.95)] if durations else 0

    # Disease distribution
    diseases = session.query(Prediction.disease, func.count(Prediction.id)).group_by(Prediction.disease).all()
    disease_dist = [{"name": d[0] or "Unknown", "value": d[1]} for d in diseases if d[0]]

    # Confidence brackets
    high_conf = session.query(func.count(Prediction.id)).filter(Prediction.disease_conf >= 0.75).scalar() or 0
    med_conf = session.query(func.count(Prediction.id)).filter(Prediction.disease_conf >= 0.50, Prediction.disease_conf < 0.75).scalar() or 0
    low_conf = session.query(func.count(Prediction.id)).filter(Prediction.disease_conf < 0.50).scalar() or 0

    return {
        "total_users": total_users,
        "total_scans": total_scans,
        "completed_scans": total_completed,
        "accuracy": accuracy,
        "queue_depth": total_processing,
        "failures": {
            "total_failed": total_failed,
            "failure_rate": failure_rate,
        },
        "processing_duration": {
            "avg_ms": avg_duration_ms,
            "p95_ms": p95_duration_ms,
            "sample_count": len(durations),
        },
        "fallbacks": {
            "recommendation_fallbacks": rec_fallbacks,
            "weather_fallbacks": weather_fallbacks,
        },
        "expert_metrics": {
            "total_reviews": expert_total,
            "approved": expert_approved,
            "overrides": expert_overrides,
            "pending": expert_pending,
            "validated_accuracy": expert_validated_accuracy,
        },
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
            "review_status": f.review_status,
            "review_decision": f.review_decision,
            "reviewer_id": f.reviewer_id,
            "reviewer_note": f.reviewer_note,
            "reviewed_at": f.reviewed_at.isoformat() if f.reviewed_at else None,
            "created_at": str(f.created_at)
        })
    return results

from pydantic import BaseModel
import json
from pathlib import Path

import yaml

CONFIG_PATH = settings.CONFIG_PATH

class ConfigPayload(BaseModel):
    crop_routing_threshold: float
    expert_escalation_cutoff: float

def get_config():
    if not CONFIG_PATH.exists():
        return {"crop_routing_threshold": 0.75, "expert_escalation_cutoff": 0.70}
    with CONFIG_PATH.open("r", encoding='utf-8') as f:
        data = yaml.safe_load(f)
        return {
            "crop_routing_threshold": data.get("thresholds", {}).get("crop_confidence", 0.75),
            "expert_escalation_cutoff": data.get("thresholds", {}).get("disease_confidence", 0.70)
        }

@router.get("/config")
async def read_config(is_admin: bool = Depends(require_admin_role)):
    return get_config()

@router.put("/config")
async def update_config(payload: ConfigPayload, is_admin: bool = Depends(require_admin_role)):
    if not CONFIG_PATH.exists():
        raise HTTPException(status_code=404, detail="config.yaml not found")
        
    with CONFIG_PATH.open("r", encoding='utf-8') as f:
        data = yaml.safe_load(f)
        
    if "thresholds" not in data:
        data["thresholds"] = {}
        
    data["thresholds"]["crop_confidence"] = payload.crop_routing_threshold
    data["thresholds"]["disease_confidence"] = payload.expert_escalation_cutoff
    
    with CONFIG_PATH.open("w", encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
    return get_config()

@router.delete("/blobs")
async def purge_blobs(is_admin: bool = Depends(require_admin_role), session: Session = Depends(get_session)):
    from app.models.image import Image
    from pathlib import Path
    
    # Get all DB image paths
    db_images = session.query(Image).all()
    valid_paths = set()
    for img in db_images:
        if img.raw_path:
            valid_paths.add(img.raw_path.replace("\\", "/"))
        if img.processed_path:
            valid_paths.add(img.processed_path.replace("\\", "/"))
            
    deleted_count = 0
    # Walk image storage and the generated audio cache.
    ensure_storage_directories()
    directories_to_clean = [settings.UPLOAD_ROOT, settings.PROCESSED_ROOT, settings.AUDIO_ROOT]
    
    for dir_path in directories_to_clean:
        folder = Path(dir_path)
        if folder.exists():
            for file in folder.glob("*"):
                if file.is_file():
                    # The DB stores them as 'data/uploads/filename.jpg'
                    rel_path = storage_relative_path(file)
                    if rel_path not in valid_paths:
                        file.unlink()
                        deleted_count += 1
                        
    return {"status": "success", "deleted_files": deleted_count}

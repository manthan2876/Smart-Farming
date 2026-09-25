from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from pydantic import BaseModel
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


def _compute_drift_metrics(session: Session) -> dict[str, Any]:
    """Compute production drift signals for the admin metrics endpoint.

    Returns:
        avg_disease_confidence_7d  — rolling 7-day average disease confidence
        avg_disease_confidence_30d — rolling 30-day average disease confidence
        low_confidence_rate_7d     — % of predictions in last 7d below disease threshold
        retraining_candidates      — pending DatasetCandidate count
        expert_correction_rate     — % of expert reviews that resulted in a correction
    """
    from datetime import timedelta
    from sqlalchemy import func as sqlfunc
    from app.core.config import settings

    now_utc = datetime.now(timezone.utc)
    cutoff_7d  = now_utc - timedelta(days=7)
    cutoff_30d = now_utc - timedelta(days=30)

    # Import here to avoid circular imports at module level
    from app.models import Prediction as Pred, DatasetCandidate, ExpertReview

    threshold = settings.DISEASE_CONFIDENCE_THRESHOLD

    # Average confidence over last 7 and 30 days
    avg_7d = session.query(sqlfunc.avg(Pred.disease_conf)).filter(
        Pred.created_at >= cutoff_7d,
        Pred.disease_conf.isnot(None),
    ).scalar()

    avg_30d = session.query(sqlfunc.avg(Pred.disease_conf)).filter(
        Pred.created_at >= cutoff_30d,
        Pred.disease_conf.isnot(None),
    ).scalar()

    # Low confidence rate in last 7 days
    total_7d = session.query(sqlfunc.count(Pred.id)).filter(
        Pred.created_at >= cutoff_7d,
        Pred.disease_conf.isnot(None),
    ).scalar() or 0

    low_7d = session.query(sqlfunc.count(Pred.id)).filter(
        Pred.created_at >= cutoff_7d,
        Pred.disease_conf < threshold,
        Pred.disease_conf.isnot(None),
    ).scalar() or 0

    low_conf_rate = round((low_7d / total_7d * 100), 1) if total_7d else None

    # Retraining candidates
    retraining_candidates = session.query(sqlfunc.count(DatasetCandidate.id)).filter(
        DatasetCandidate.status == "pending_review"
    ).scalar() or 0

    # Expert correction rate: reviews where decision includes "Override" or corrected_disease was set
    total_reviews = session.query(sqlfunc.count(ExpertReview.id)).filter(
        ExpertReview.status == "verified"
    ).scalar() or 0

    correction_reviews = session.query(sqlfunc.count(ExpertReview.id)).filter(
        ExpertReview.status == "verified",
        ExpertReview.corrected_disease.isnot(None),
    ).scalar() or 0

    expert_correction_rate = round((correction_reviews / total_reviews * 100), 1) if total_reviews else None

    return {
        "avg_disease_confidence_7d": round(float(avg_7d), 4) if avg_7d is not None else None,
        "avg_disease_confidence_30d": round(float(avg_30d), 4) if avg_30d is not None else None,
        "low_confidence_rate_7d": low_conf_rate,
        "predictions_last_7d": total_7d,
        "low_confidence_last_7d": low_7d,
        "retraining_candidates": retraining_candidates,
        "expert_correction_rate": expert_correction_rate,
        "confidence_threshold": threshold,
    }


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
        ],
        "drift": _compute_drift_metrics(session),
    }


class AdminPurgeRequest(BaseModel):
    confirmation: str | None = None


@router.delete("/purge")
async def purge_database(
    payload: AdminPurgeRequest | None = Body(None),
    confirmation: str | None = Query(None),
    dry_run: bool = False,
    user_id: str = Depends(require_admin_role),
    session: Session = Depends(get_session)
) -> dict[str, Any]:
    token = None
    if payload and payload.confirmation:
        token = payload.confirmation.strip().upper()
    elif confirmation:
        token = confirmation.strip().upper()

    valid_tokens = {"PURGE_ALL_DATA", "DELETE"}
    if token and token not in valid_tokens:
        raise HTTPException(
            status_code=400,
            detail="Confirmation token mismatch. Must provide 'DELETE' or 'PURGE_ALL_DATA' to confirm.",
        )
    if dry_run:
        counts = {
            "dataset_candidates": session.query(func.count(DatasetCandidate.id)).scalar() or 0,
            "expert_reviews": session.query(func.count(ExpertReview.id)).scalar() or 0,
            "recommendations": session.query(func.count(Recommendation.id)).scalar() or 0,
            "feedback": session.query(func.count(Feedback.id)).scalar() or 0,
            "alerts": session.query(func.count(Alert.id)).scalar() or 0,
            "predictions": session.query(func.count(Prediction.id)).scalar() or 0,
            "images": session.query(func.count(Image.id)).scalar() or 0,
        }
        return {"status": "dry_run", "message": "Records that would be purged", "counts": counts}

    session.execute(sa.delete(DatasetCandidate))
    session.execute(sa.delete(ExpertReview))
    session.execute(sa.delete(Recommendation))
    session.execute(sa.delete(Feedback))
    session.execute(sa.delete(Alert))
    session.execute(sa.delete(Prediction))
    session.execute(sa.delete(Image))
    session.commit()
    return {"status": "success", "message": "Database wiped successfully."}



# --------------------------------------------------------------------------------------
# Admin User Management & Role Switching
# --------------------------------------------------------------------------------------
class AdminRoleUpdateRequest(BaseModel):
    role: str
    reason: str | None = None


@router.get("/users")
async def get_users_list(
    skip: int = 0,
    limit: int = 50,
    role: str | None = None,
    search: str | None = None,
    caller_id: str = Depends(require_admin_role),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """List registered users with role filtering, search, and pagination."""
    query = session.query(User)
    if role and role.strip() and role.strip().lower() != "all":
        query = query.filter(User.role == role.strip().lower())
    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        query = query.filter(
            sa.or_(
                sa.func.lower(User.name).like(term),
                sa.func.lower(User.email).like(term),
                sa.func.lower(User.phone).like(term),
            )
        )
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    results = []
    for u in users:
        farm = u.farm
        results.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "phone": u.phone,
            "role": u.role,
            "language": u.language,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "deleted_at": u.deleted_at.isoformat() if u.deleted_at else None,
            "scan_count": len(u.predictions) if u.predictions else 0,
            "farm_name": farm.name if farm else None,
            "farm_location": farm.location if farm else None,
        })
    return {"total": total, "users": results}


@router.patch("/users/{target_user_id}/role")
async def update_user_role(
    target_user_id: str,
    payload: AdminRoleUpdateRequest,
    caller_id: str = Depends(require_admin_role),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """
    Change user role (farmer, expert, admin).
    Lockout Protections:
    - An admin cannot demote their own account.
    - An admin cannot demote the last remaining active administrator on the platform.
    """
    allowed_roles = {"farmer", "expert", "admin"}
    new_role = payload.role.strip().lower()
    if new_role not in allowed_roles:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid role '{payload.role}'. Allowed roles: {sorted(list(allowed_roles))}",
        )

    target_user = session.get(User, target_user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found.")

    # Guard 1: Self-demotion lockout prevention
    if target_user_id == caller_id and new_role != "admin":
        raise HTTPException(
            status_code=400,
            detail="Security violation: Administrators cannot demote their own account.",
        )

    # Guard 2: Last admin demotion prevention
    if target_user.role == "admin" and new_role != "admin":
        active_admins = session.query(func.count(User.id)).filter(User.role == "admin").scalar() or 0
        if active_admins <= 1:
            raise HTTPException(
                status_code=400,
                detail="Operation blocked: Cannot demote the last remaining administrator on the platform.",
            )

    old_role = target_user.role
    target_user.role = new_role
    session.add(target_user)
    session.commit()
    session.refresh(target_user)

    return {
        "status": "success",
        "user_id": target_user_id,
        "old_role": old_role,
        "new_role": new_role,
        "reason": payload.reason,
    }


# --------------------------------------------------------------------------------------
# Proactive Weather Risk Manual Trigger
# --------------------------------------------------------------------------------------
@router.post("/weather-risk/trigger")
async def trigger_weather_risk_job(caller_id: str = Depends(require_admin_role)) -> dict[str, Any]:
    """Manually trigger proactive weather risk alert job for all farms."""
    from app.services.weather.proactive import evaluate_weather_risks
    result = await evaluate_weather_risks(None)
    return {"status": "success", "result": result or "Completed"}


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
        data = yaml.safe_load(f) or {}
        return {
            "crop_routing_threshold": data.get("thresholds", {}).get("crop_confidence", 0.75),
            "expert_escalation_cutoff": data.get("thresholds", {}).get("disease_confidence", 0.70)
        }

@router.get("/config")
async def read_config(is_admin: bool = Depends(require_admin_role)):
    return get_config()

@router.put("/config")
async def update_config(payload: ConfigPayload, is_admin: bool = Depends(require_admin_role)):
    if payload.crop_routing_threshold < 0.05 or payload.crop_routing_threshold > 0.99:
        raise HTTPException(status_code=422, detail="crop_routing_threshold must be between 0.05 and 0.99")
    if payload.expert_escalation_cutoff < 0.05 or payload.expert_escalation_cutoff > 0.99:
        raise HTTPException(status_code=422, detail="expert_escalation_cutoff must be between 0.05 and 0.99")

    if not CONFIG_PATH.exists():
        raise HTTPException(status_code=404, detail="config.yaml not found")
        
    with CONFIG_PATH.open("r", encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
        
    if "thresholds" not in data:
        data["thresholds"] = {}
        
    data["thresholds"]["crop_confidence"] = payload.crop_routing_threshold
    data["thresholds"]["disease_confidence"] = payload.expert_escalation_cutoff
    
    with CONFIG_PATH.open("w", encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    # Hot-reload in-process
    try:
        from app import pipeline
        pipeline.reload_config()
    except Exception as exc:
        pass

    # Publish to Upstash Redis REST for serverless multi-instance sync
    try:
        from app.core.redis_rest import redis_rest
        await redis_rest.set(
            "sf:config:thresholds",
            data.get("thresholds", {}),
        )
    except Exception:
        pass
        
    return get_config()

@router.delete("/blobs")
async def purge_blobs(
    dry_run: bool = False,
    is_admin: bool = Depends(require_admin_role),
    session: Session = Depends(get_session)
):
    from app.core.storage import purge_orphaned_blobs
    return purge_orphaned_blobs(session, dry_run=dry_run, grace_seconds=0)


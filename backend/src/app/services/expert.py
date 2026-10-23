from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.core.config import settings
from app.crud.expert_review import (
    get_pending_reviews,
    get_review_by_id,
    claim_review,
    release_review,
)
from app.models import Alert, DatasetCandidate, ExpertReview
from app.schemas.expert import ExpertReviewSubmissionRequest
from app.services.translation.overlay import overlay_dict_translations

logger = logging.getLogger("smart-farming.services.expert")

LEASE_DURATION_SECONDS = 900


def get_queue_items(session: Session) -> list[dict[str, Any]]:
    """Retrieve formatted expert queue items."""
    reviews = get_pending_reviews(session)
    results = []
    for r in reviews:
        pred = r.prediction
        result_json = pred.result or {} if pred else {}

        crop = result_json.get("crop", {}).get("label") or (pred.crop if pred else "Unknown")
        disease = result_json.get("disease", {}).get("label") or (pred.disease if pred else "Unknown")
        disease_conf = result_json.get("disease", {}).get("confidence") or (pred.disease_conf if pred else None)
        severity_pct = result_json.get("severity", {}).get("percent") or (pred.severity_pct if pred else None)

        results.append({
            "id": r.id,
            "review_id": r.id,
            "prediction_id": r.prediction_id,
            "status": r.status,
            "crop": crop,
            "disease": disease,
            "disease_conf": disease_conf,
            "confidence": disease_conf,
            "severity_pct": severity_pct,
            "claimed_by": r.claimed_by,
            "claimed_at": r.claimed_at.isoformat() if r.claimed_at else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return results


def get_review_detail(
    session: Session,
    review_id: int,
    lang: str | None = None,
    accept_language: str | None = None,
) -> dict[str, Any]:
    """Retrieve full expert review detail including media URLs and optional translation overlay."""
    review = get_review_by_id(session, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    pred = review.prediction
    result_json = pred.result or {} if pred else {}

    crop = result_json.get("crop", {}).get("label") or (pred.crop if pred else "Unknown")
    disease = result_json.get("disease", {}).get("label") or (pred.disease if pred else "Unknown")
    disease_conf = result_json.get("disease", {}).get("confidence") or (pred.disease_conf if pred else None)
    severity_pct = result_json.get("severity", {}).get("percent") or (pred.severity_pct if pred else None)

    raw_path = pred.raw_path or (pred.image.raw_path if pred and pred.image else None) if pred else None
    proc_path = pred.processed_path or (pred.image.processed_path if pred and pred.image else None) if pred else None

    raw_url = None
    processed_url = None
    if getattr(settings, "STORAGE_BACKEND", "local").lower() in ("supabase", "s3"):
        try:
            from app.core.storage import get_storage
            storage = get_storage()
            expiry = settings.SUPABASE_SIGNED_URL_EXPIRY_SECONDS
            if raw_path:
                raw_url = storage.get_url(raw_path, expires_in=expiry)
            if proc_path:
                processed_url = storage.get_url(proc_path, expires_in=expiry)
        except Exception:
            pass

    data = {
        "review_id": review.id,
        "prediction_id": review.prediction_id,
        "status": review.status,
        "decision": review.decision,
        "corrected_disease": review.corrected_disease,
        "farmer_guidance": review.farmer_guidance,
        "internal_note": review.internal_note,
        "raw_path": raw_path,
        "processed_path": proc_path,
        "raw_url": raw_url,
        "processed_url": processed_url,
        "crop": crop,
        "disease": disease,
        "disease_conf": disease_conf,
        "severity_pct": severity_pct,
        "created_at": review.created_at.isoformat() if review.created_at else None,
    }
    req_lang = lang or accept_language
    overlay_dict_translations(session, data, "expert_review", review.id, ["farmer_guidance"], req_lang)
    return data


def claim_review_lease(session: Session, review_id: int, user_id: str) -> dict[str, Any]:
    """Atomically claims a review item for 15 minutes to prevent expert collisions."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=LEASE_DURATION_SECONDS)

    review = get_review_by_id(session, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.status != "pending":
        raise HTTPException(status_code=409, detail="Review is already verified and finalized.")

    claimed_dt = review.claimed_at
    if claimed_dt and claimed_dt.tzinfo is None:
        claimed_dt = claimed_dt.replace(tzinfo=timezone.utc)

    if review.claimed_by and review.claimed_by != user_id:
        if claimed_dt and claimed_dt > cutoff:
            remaining_secs = int(LEASE_DURATION_SECONDS - (now - claimed_dt).total_seconds())
            raise HTTPException(
                status_code=409,
                detail=f"Review is currently claimed by another expert ({review.claimed_by}). Lease expires in {remaining_secs}s.",
            )

    claim_review(session, review, user_id)
    return {
        "status": "claimed",
        "review_id": review_id,
        "claimed_by": user_id,
        "lease_expires_in_seconds": LEASE_DURATION_SECONDS,
    }


def release_review_lease(session: Session, review_id: int, user_id: str) -> dict[str, Any]:
    """Releases a claimed review item back to the shared queue."""
    review = get_review_by_id(session, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.claimed_by == user_id:
        release_review(session, review)
    return {"status": "released", "review_id": review_id}


def submit_review_decision(
    session: Session,
    review_id: int,
    user_id: str,
    payload: ExpertReviewSubmissionRequest,
) -> tuple[dict[str, Any], Alert | None, str | None]:
    """
    Validates state machine transitions, claim lease, and records expert verdict.
    Returns (result_dict, created_alert_or_none, farmer_guidance_for_translation).
    """
    review = get_review_by_id(session, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="Conflict: This review has already been verified and finalized.",
        )

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=LEASE_DURATION_SECONDS)
    claimed_dt = review.claimed_at
    if claimed_dt and claimed_dt.tzinfo is None:
        claimed_dt = claimed_dt.replace(tzinfo=timezone.utc)

    if review.claimed_by and review.claimed_by != user_id:
        if claimed_dt and claimed_dt > cutoff:
            raise HTTPException(
                status_code=409,
                detail=f"Conflict: This review is currently claimed by another expert ({review.claimed_by}).",
            )

    action = payload.action or payload.decision or "Confirm AI Findings"
    review.decision = action
    review.status = "verified"
    review.expert_id = user_id
    review.claimed_by = None
    review.claimed_at = None

    if action in ("Override / Correct Findings", "corrected", "override", "Override") or payload.corrected_disease:
        review.corrected_disease = payload.corrected_disease
        raw_sev = payload.corrected_severity
        if raw_sev is not None:
            if isinstance(raw_sev, (int, float)):
                review.corrected_severity = float(raw_sev)
            elif isinstance(raw_sev, str):
                import re
                m = re.search(r"\d+(\.\d+)?", raw_sev)
                if m:
                    review.corrected_severity = float(m.group(0))

    review.farmer_guidance = payload.farmer_guidance
    review.internal_note = payload.internal_note
    review.reviewed_at = now

    pred = review.prediction
    if not pred:
        raise HTTPException(status_code=404, detail="Associated prediction not found")

    pred.status = "rescan_requested" if action == "Request Rescan" else "verified"

    new_alert = None
    if not session.query(Alert).filter(
        Alert.prediction_id == pred.id,
        Alert.kind == "review_verified",
    ).first():
        new_alert = Alert(
            user_id=pred.user_id,
            prediction_id=pred.id,
            kind="review_verified",
            severity="high",
            title=f"Expert Review Completed for Scan #{pred.id}",
            body=f"An agronomist has verified your scan. Conclusion: {action}.",
        )
        session.add(new_alert)

    if payload.add_to_retraining:
        orig_disease = pred.result.get("disease", {}).get("label") if pred.result else pred.disease
        corrected = review.corrected_disease or orig_disease
        if not session.query(DatasetCandidate).filter(DatasetCandidate.prediction_id == pred.id).first():
            provenance = (
                f"Expert {user_id} reviewed prediction #{pred.id} with action '{action}'."
                + (f" Corrected label: {corrected}." if corrected != orig_disease else "")
            )
            session.add(DatasetCandidate(
                prediction_id=pred.id,
                source="expert_correction",
                original_label=orig_disease,
                corrected_label=corrected,
                image_path=pred.image.raw_path if pred.image else "",
                status="pending_review",
                provenance_note=provenance,
            ))

    res = dict(pred.result or {})
    result_status = dict(res.get("status") or {})

    if action == "Request Rescan":
        result_status["expert_review"] = "rescan_requested"
        result_status["pipeline"] = "rescan_requested"
        pred.status = "rescan_requested"
    else:
        result_status["expert_review"] = "verified"
        result_status["pipeline"] = "verified"
        pred.status = "verified"
        result_status["mask_advisory"] = False

    res["status"] = result_status

    if review.farmer_guidance:
        if "recommendation" not in res:
            res["recommendation"] = {}
        res["recommendation"]["expert_verified_advisory"] = review.farmer_guidance

    if review.corrected_disease:
        res.setdefault("disease", {})["label"] = review.corrected_disease
        res["disease"]["is_uncertain"] = False
        res["disease"]["confidence_rating"] = "verified"
        pred.disease = review.corrected_disease
    elif action == "Confirm AI Findings":
        res.setdefault("disease", {})["is_uncertain"] = False
        res["disease"]["confidence_rating"] = "verified"

    if review.corrected_severity is not None:
        res.setdefault("severity", {})["percent"] = review.corrected_severity
        sev_bucket = "Severe" if review.corrected_severity > 55 else ("Moderate" if review.corrected_severity >= 25 else "Low")
        res["severity"]["bucket"] = sev_bucket
        pred.severity_pct = review.corrected_severity
        if hasattr(pred, "severity_bucket"):
            pred.severity_bucket = sev_bucket

    res["expert_review_data"] = {
        "decision": action,
        "corrected_disease": review.corrected_disease,
        "corrected_severity": review.corrected_severity,
        "farmer_guidance": review.farmer_guidance,
        "status": "verified",
        "reviewed_at": review.reviewed_at.isoformat() if review.reviewed_at else None,
    }

    pred.result = res
    flag_modified(pred, "result")
    session.commit()

    return {"status": "success", "review_id": review_id}, new_alert, review.farmer_guidance

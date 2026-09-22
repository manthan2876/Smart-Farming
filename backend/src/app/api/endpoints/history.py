from __future__ import annotations

import uuid
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas import PredictionResponse
from app.api.deps import get_current_user
from app.core import get_session
from app.crud import list_predictions

router = APIRouter()

from datetime import datetime, timezone
import sqlalchemy as sa
from app.models import Prediction


@router.get("/history")
async def history(
    offset: int = 0,
    limit: int = 20,
    crop: str | None = None,
    disease: str | None = None,
    status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    plot_id: int | None = None,
    last_id: int | None = None,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[dict[str, Any]]:
    if offset < 0 or limit < 1 or limit > 100:
        raise HTTPException(
            status_code=422,
            detail="offset must be non-negative and limit must be 1-100.",
        )
    try:
        query = session.query(Prediction).filter(Prediction.user_id == user_id)
        if crop and crop.strip():
            query = query.filter(sa.func.lower(Prediction.crop) == crop.strip().lower())
        if disease and disease.strip():
            query = query.filter(sa.func.lower(Prediction.disease).like(f"%{disease.strip().lower()}%"))
        if status and status.strip():
            query = query.filter(Prediction.status == status.strip().lower())
        if plot_id is not None:
            query = query.filter(Prediction.plot_id == plot_id)
        if start_date:
            try:
                dt_start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                query = query.filter(Prediction.created_at >= dt_start)
            except Exception:
                pass
        if end_date:
            try:
                dt_end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                query = query.filter(Prediction.created_at <= dt_end)
            except Exception:
                pass
        if last_id is not None:
            query = query.filter(Prediction.id < last_id)

        predictions = query.order_by(Prediction.id.desc()).offset(offset if last_id is None else 0).limit(limit).all()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail=f"DB Error: {str(exc)}") from exc
        
    results = []
    for p in predictions:
        res = dict(p.result or {})
        res["prediction_id"] = p.id
        res["id"] = p.id

        # Normalize crop: must be a dictionary matching PredictionResponse & clients
        existing_crop = res.get("crop")
        if isinstance(existing_crop, dict) and existing_crop.get("label"):
            pass
        elif isinstance(existing_crop, str) and existing_crop:
            res["crop"] = {
                "label": existing_crop,
                "confidence": p.crop_conf if p.crop_conf is not None else 1.0,
            }
        else:
            res["crop"] = {
                "label": p.crop or "Unknown crop",
                "confidence": p.crop_conf if p.crop_conf is not None else 0.0,
            }

        # Normalize disease: must be a dictionary
        existing_disease = res.get("disease")
        if isinstance(existing_disease, dict) and existing_disease.get("label"):
            pass
        elif isinstance(existing_disease, str) and existing_disease:
            res["disease"] = {
                "label": existing_disease,
                "confidence": p.disease_conf if p.disease_conf is not None else 1.0,
            }
        else:
            res["disease"] = {
                "label": p.disease or ("Processing Failed" if p.status == "failed" else "Unknown condition"),
                "confidence": p.disease_conf if p.disease_conf is not None else 0.0,
            }

        # Normalize severity: must be a dictionary
        existing_sev = res.get("severity")
        if isinstance(existing_sev, dict) and (existing_sev.get("percent") is not None or existing_sev.get("bucket")):
            pass
        elif isinstance(existing_sev, (int, float)):
            res["severity"] = {
                "percent": float(existing_sev),
                "bucket": "Moderate" if existing_sev > 30 else "Mild",
            }
        else:
            sev_pct = p.severity_pct if p.severity_pct is not None else 0.0
            res["severity"] = {
                "percent": sev_pct,
                "bucket": "Severe" if sev_pct > 60 else "Moderate" if sev_pct > 25 else "Low",
            }

        # Normalize image: must be a dictionary
        existing_img = res.get("image")
        if not isinstance(existing_img, dict):
            res["image"] = {
                "raw_path": p.raw_path,
                "processed_path": p.processed_path,
            }
        else:
            if not existing_img.get("raw_path") and p.raw_path:
                existing_img["raw_path"] = p.raw_path
            if not existing_img.get("processed_path") and p.processed_path:
                existing_img["processed_path"] = p.processed_path

        # Normalize status
        if isinstance(res.get("status"), dict):
            res["status"]["pipeline"] = p.status
        else:
            res["status"] = {"pipeline": p.status}

        # Normalize recommendation
        if "recommendation" not in res or not isinstance(res.get("recommendation"), (dict, str)):
            res["recommendation"] = {
                "summary": "Follow recommended agricultural treatments.",
            }

        res["created_at"] = p.created_at.isoformat() if p.created_at else None
        results.append(res)

    return results


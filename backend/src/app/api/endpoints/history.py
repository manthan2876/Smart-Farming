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

@router.get("/history")
async def history(
    offset: int = 0,
    limit: int = 20,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[dict[str, Any]]:
    if offset < 0 or limit < 1 or limit > 100:
        raise HTTPException(
            status_code=422,
            detail="offset must be non-negative and limit must be 1-100.",
        )
    try:
        predictions = list_predictions(session, user_id, offset, limit)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail=f"DB Error: {str(exc)}") from exc
        
    results = []
    for p in predictions:
        res = dict(p.result)
        res["prediction_id"] = p.id
        res["created_at"] = p.created_at.isoformat() if p.created_at else None
        results.append(res)
        
    return results

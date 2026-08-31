from __future__ import annotations

import uuid
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas import PredictionResponse
from app.api import get_current_user, get_session
from app.crud import list_predictions

router = APIRouter()

@router.get("/history", response_model=list[PredictionResponse])
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
        # <-- TEMPORARY DEBUG PRINT -->
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=503, detail=f"DB Error: {str(exc)}") from exc
    return [
        {**prediction.result, "prediction_id": prediction.id}
        for prediction in predictions
    ]
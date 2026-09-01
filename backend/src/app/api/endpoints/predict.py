from __future__ import annotations

import uuid
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api import _json_safe, get_current_user, get_session
from app.schemas import PredictionResponse, ErrorResponse
from app.context import create_context
from app.pipeline import run_pipeline
from app.utils import prediction_event
from app.crud import record_prediction, get_prediction

router = APIRouter()

_BACKEND_DIR = Path(__file__).resolve().parents[4]
_UPLOAD_DIR = _BACKEND_DIR / "data" / "uploads"
if not _UPLOAD_DIR.parent.exists():
    _UPLOAD_DIR = Path.cwd() / "data" / "uploads"
_MAX_UPLOAD_BYTES = 10 * 1024 * 1024
_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
_LOGGER = logging.getLogger("smart-farming.api")


def _public_result(context: dict[str, Any]) -> dict[str, Any]:
    public_context = {
        key: value for key, value in context.items() if not key.startswith("_")
    }
    public_context["image"] = {
        key: value
        for key, value in public_context.get("image", {}).items()
        if key != "leaf_crop"
    }
    return _json_safe(public_context)

@router.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        401: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        415: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
async def predict(
    file: UploadFile = File(...),
    location: str = Form(default="Unknown"),
    lat: float = Form(default=52.2297),
    lon: float = Form(default=21.0122),
    language: str = Form(default="English"),
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Upload a JPEG, PNG, or WebP image.",
        )

    suffix = Path(file.filename or "upload.jpg").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg" if file.content_type == "image/jpeg" else ".png"
    
    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{suffix}"
    upload_path = _UPLOAD_DIR / filename
    
    # Clean relative path format with forward slashes for database storage
    relative_image_path = f"data/uploads/{filename}"

    size = 0
    try:
        with upload_path.open("wb") as destination:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > _MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Image exceeds the 10 MB upload limit.",
                    )
                destination.write(chunk)

        # Absolute path is required here so the pipeline/preprocessing can read the file from disk
        context = create_context(
            image_path=str(upload_path),
            user_id=user_id,
            location=location,
            lat=lat,
            lon=lon,
            language=language,
        )
        result = run_pipeline(context)
        
        prediction_event(
            _LOGGER,
            "pipeline_completed",
            request_id=result.get("request_id"),
            user_id=user_id,
            preprocessing_status=result.get("status", {}).get("preprocessing"),
        )
        preprocessing_status = result.get("status", {}).get("preprocessing")
        if preprocessing_status != "completed":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Image quality check failed; please upload a clearer leaf image.",
                headers={"X-Pipeline-Status": str(preprocessing_status)},
            )

        # Overwrite the absolute path with the clean relative path in the result dictionary
        if "image" in result and isinstance(result["image"], dict):
            result["image"]["raw_path"] = relative_image_path

        public_result = _public_result(result)
        
        try:
            prediction = record_prediction(session, user_id, public_result)
            
            # Directly override database record attributes if stored in dedicated table columns
            if hasattr(prediction, "image_path"):
                prediction.image_path = relative_image_path
                session.commit()
                
        except SQLAlchemyError as exc:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Prediction completed, but the database is unavailable.",
            ) from exc
            
        public_result["prediction_id"] = prediction.id
        prediction_event(
            _LOGGER,
            "prediction_logged",
            request_id=public_result.get("request_id"),
            prediction_id=prediction.id,
            user_id=user_id,
        )
        return public_result
    finally:
        await file.close()

@router.get("/predictions/{prediction_id}", response_model=PredictionResponse)
async def prediction_detail(
    prediction_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    try:
        prediction = get_prediction(session, prediction_id, user_id)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found.")
    result = dict(prediction.result)
    result["prediction_id"] = prediction.id
    return result
from __future__ import annotations

import uuid
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user
from backend.api.schemas import (
    CropListResponse,
    ErrorResponse,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    PredictionResponse,
)
from backend.context import create_context
from backend.database.repository import add_feedback, get_prediction, list_predictions, record_prediction
from backend.database.session import get_session
from backend.pipeline import run_pipeline
from backend.utils.logging import prediction_event

router = APIRouter()

_BACKEND_DIR = Path(__file__).resolve().parents[1]
_UPLOAD_DIR = _BACKEND_DIR / "data" / "uploads"
_MAX_UPLOAD_BYTES = 10 * 1024 * 1024
_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
_LOGGER = logging.getLogger("smart-farming.api")


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items() if not str(key).startswith("_")}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "tolist"):
        return _json_safe(value.tolist())
    return str(value)


def _public_result(context: dict[str, Any]) -> dict[str, Any]:
    public_context = {key: value for key, value in context.items() if not key.startswith("_")}
    public_context["image"] = {
        key: value
        for key, value in public_context.get("image", {}).items()
        if key != "leaf_crop"
    }
    return _json_safe(public_context)


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="smart-farming-backend")


@router.get("/crops", response_model=CropListResponse)
async def crops() -> CropListResponse:
    from backend.pipeline import _CONFIG

    configured = _CONFIG.get("models", {}).get("disease_models", {})
    return CropListResponse(crops=sorted(str(crop) for crop in configured))


@router.get("/weather")
async def weather(
    lat: float = 52.2297,
    lon: float = 21.0122,
    user_id: str = Depends(get_current_user),
) -> dict[str, Any]:
    from backend.services.weather.service import fetch_weather

    context = create_context(
        image_path="",
        user_id=user_id,
        lat=lat,
        lon=lon,
    )
    result = fetch_weather(context, {})
    return _json_safe(result.get("weather", {}))


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
    upload_path = _UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}"

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
        public_result = _public_result(result)
        try:
            prediction = record_prediction(session, user_id, public_result)
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


@router.get("/history", response_model=list[PredictionResponse])
async def history(
    offset: int = 0,
    limit: int = 20,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[dict[str, Any]]:
    if offset < 0 or limit < 1 or limit > 100:
        raise HTTPException(status_code=422, detail="offset must be non-negative and limit must be 1-100.")
    try:
        predictions = list_predictions(session, user_id, offset, limit)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    return [{**prediction.result, "prediction_id": prediction.id} for prediction in predictions]


@router.post("/feedback", response_model=FeedbackResponse, status_code=201)
async def feedback(
    payload: FeedbackRequest,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> FeedbackResponse:
    try:
        prediction = get_prediction(session, payload.prediction_id, user_id)
        if prediction is None:
            raise HTTPException(status_code=404, detail="Prediction not found.")
        saved = add_feedback(session, prediction, payload.is_correct, payload.farmer_note)
        prediction_event(
            _LOGGER,
            "feedback_recorded",
            prediction_id=saved.prediction_id,
            user_id=user_id,
            is_correct=saved.is_correct,
        )
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    return FeedbackResponse(
        id=saved.id,
        prediction_id=saved.prediction_id,
        is_correct=saved.is_correct,
        farmer_note=saved.farmer_note,
    )


@router.get("/admin/metrics", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def metrics_placeholder() -> dict[str, str]:
    raise HTTPException(status_code=501, detail="Metrics are scheduled for Stage 16.")

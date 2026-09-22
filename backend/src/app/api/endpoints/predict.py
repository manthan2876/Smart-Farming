from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.context import create_context
from app.core import get_session
from app.core.config import settings
from app.core.limiter import limiter
from app.core.paths import ensure_storage_directories, storage_relative_path
from app.crud import get_prediction, record_prediction
from app.crud.expert_review import ensure_expert_review
from app.schemas import ErrorResponse, PredictionResponse
from app.services.prediction_job import _public_result

router = APIRouter()

_UPLOAD_DIR = settings.UPLOAD_ROOT
_MAX_UPLOAD_BYTES = settings.UPLOAD_MAX_BYTES
_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
_LOGGER = logging.getLogger("smart-farming.api")

# DB `Prediction.status` values that mean the pipeline finished successfully.
_SUCCESS_STATUSES = {"ready", "completed", "verified", "pending_expert_review"}


# --------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------
def _apply_pipeline_status(result: dict[str, Any], db_status: str | None) -> dict[str, Any]:
    """Make ``result["status"]["pipeline"]`` agree with the authoritative DB status.

    The JSON snapshot can lag behind (or omit the key mid-run), and a failed prediction must
    never be reported as "completed". Works on a copy of the status dict so the ORM object's
    nested JSON is never mutated in place.
    """
    state = dict(result.get("status") or {})
    if db_status == "failed":
        state["pipeline"] = "failed"
    elif db_status in _SUCCESS_STATUSES:
        state["pipeline"] = "completed"
    elif db_status == "processing":
        state["pipeline"] = "processing"
    result["status"] = state
    return result


def _placeholder_result(user_id: str, relative_image_path: str, suffix: str) -> dict[str, Any]:
    return {
        "request_id": str(uuid.uuid4()),
        "user": {"id": user_id},
        "image": {
            "raw_path": relative_image_path,
            "processed_path": None,
            "resolution": None,
            "channels": None,
            "quality_score": 1.0,
            "format": suffix,
        },
        "crop": {},
        "disease": {},
        "severity": {},
        "pests": [],
        "pest_classification": {},
        "weather": {},
        "recommendation": {},
        "notes": [],
        "stages": {
            "preprocessing": {"status": "completed", "message": "Initial quality check passed."},
        },
        "status": {
            "preprocessing": "completed",
            "crop_identification": "pending",
            "decision_routing": "pending",
            "disease_classification": "pending",
            "severity": "pending",
            "pest_detection": "pending",
            "weather": "pending",
            "recommendation": "pending",
            "persistence": "pending",
            "pipeline": "processing",
            "expert_review": "not_requested",
        },
    }


async def _enqueue_prediction_job(
    request: Request,
    session: Session,
    prediction_id: int,
    user_id: str,
    relative_image_path: str,
    location: str,
    lat: float,
    lon: float,
    language: str,
    is_rescan: bool = False,
    parent_id: int | None = None,
    plot_id: int | None = None,
) -> str:
    from app.models import Prediction

    arq_pool = getattr(request.app.state, "arq_pool", None)
    if arq_pool is None:
        raise HTTPException(status_code=503, detail="Prediction worker is unavailable. Start Redis and retry.")

    try:
        job = await arq_pool.enqueue_job(
            "process_prediction_job",
            prediction_id=prediction_id,
            user_id=user_id,
            relative_image_path=relative_image_path,
            location=location,
            lat=lat,
            lon=lon,
            language=language,
            is_rescan=is_rescan,
            parent_id=parent_id,
            plot_id=plot_id,
        )
    except Exception as exc:
        prediction = session.get(Prediction, prediction_id)
        if prediction is not None:
            prediction.status = "failed"
            prediction.result = {"prediction_id": prediction_id, "error": "Unable to queue prediction for processing."}
            session.commit()
        raise HTTPException(status_code=503, detail="Unable to queue prediction for processing.") from exc

    if job is None:
        raise HTTPException(status_code=503, detail="Unable to queue prediction for processing.")
    return str(job.job_id)


def _validate_preprocessing(context: dict[str, Any], upload_path: Path, preprocessor: Any) -> dict[str, Any]:
    context = preprocessor.process(context)
    prep_status = context.get("status", {}).get("preprocessing")
    if prep_status != "completed":
        if upload_path.exists():
            try:
                upload_path.unlink()
            except OSError:
                pass

        if prep_status == "failed_blur":
            blur_score = context.get("image", {}).get("blur_score", 0.0)
            detail = (
                f"Image is too blurry (sharpness variance score: {blur_score:.1f}, "
                f"required: >= {preprocessor.blur_threshold:.1f}). Please hold the camera steady and refocus on the leaf."
            )
        elif prep_status == "failed_lighting":
            brightness = context.get("image", {}).get("brightness_score", 0.0)
            detail = (
                f"Image lighting is outside acceptable range (brightness: {brightness:.1f}, "
                f"expected between {preprocessor.min_brightness:.1f} and {preprocessor.max_brightness:.1f}). "
                f"Please retake the photo in balanced lighting."
            )
        elif prep_status == "failed_no_leaf":
            detail = (
                "No crop leaf could be detected in the image. Please center the leaf in the frame with good contrast."
            )
        else:
            detail = "Image quality check failed. Please retake the photo."

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
    return context


# --------------------------------------------------------------------------------------
# routes
# --------------------------------------------------------------------------------------
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
@limiter.limit('20/minute')
async def predict(
    request: Request,
    file: UploadFile = File(...),
    location: str = Form(default="Unknown"),
    lat: float = Form(default=52.2297),
    lon: float = Form(default=21.0122),
    language: str = Form(default="English"),
    plot_id: int | None = Form(default=None),
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        suffix = Path(file.filename or "upload.jpg").suffix.lower()
        if suffix in {".jpg", ".jpeg"}:
            file.content_type = "image/jpeg"
        elif suffix == ".png":
            file.content_type = "image/png"
        elif suffix == ".webp":
            file.content_type = "image/webp"
        else:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Upload a JPEG, PNG, or WebP image.",
            )

    suffix = Path(file.filename or "upload.jpg").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg" if file.content_type == "image/jpeg" else ".png"

    ensure_storage_directories()

    try:
        image_bytes = await file.read()
        if len(image_bytes) > _MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Image exceeds the 10 MB upload limit.",
            )

        # Magic-byte file content validation
        import io
        from PIL import Image as PILImage
        try:
            with PILImage.open(io.BytesIO(image_bytes)) as img_check:
                img_check.verify()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is not a valid or readable image.",
            )

        hash_val = hashlib.sha256(image_bytes).hexdigest()
        filename = f"{hash_val}{suffix}"
        upload_path = _UPLOAD_DIR / filename
        relative_image_path = storage_relative_path(upload_path)

        # Save to active storage backend (Local disk or AWS S3)
        from app.core.storage import get_storage
        storage = get_storage()
        storage.save(image_bytes, f"uploads/{filename}", content_type=file.content_type)

        # Ensure local disk copy exists for immediate OpenCV preprocessing
        if not upload_path.exists():
            upload_path.write_bytes(image_bytes)

        # Same image + same plot => reuse the existing prediction instead of re-running the
        # pipeline. A FAILED prediction is never served from cache, so the user can retry.
        from app.models import Image

        existing_img = session.query(Image).filter(Image.raw_path == relative_image_path).first()
        cached_pred = existing_img.prediction if existing_img else None
        if cached_pred is not None and cached_pred.plot_id == plot_id and cached_pred.status != "failed":
            pipeline_state = "processing" if cached_pred.status == "processing" else "completed"
            return {
                "job_id": None,
                "prediction_id": cached_pred.id,
                "status": {"pipeline": pipeline_state},
                # "cached" == results are already final (no live progress will ever be emitted)
                "cached": pipeline_state == "completed",
            }

        with upload_path.open("wb") as destination:
            destination.write(image_bytes)

        context = create_context(
            image_path=str(upload_path),
            user_id=user_id,
            location=location,
            lat=lat,
            lon=lon,
            language=language,
        )

        # Fast synchronous image quality check
        from app.pipeline import _PREPROCESSOR

        context = _validate_preprocessing(context, upload_path, _PREPROCESSOR)

        placeholder_result = _placeholder_result(user_id, relative_image_path, suffix)

        new_pred = record_prediction(session, user_id, placeholder_result)
        if plot_id:
            new_pred.plot_id = plot_id
        new_pred.status = "processing"
        session.commit()

        job_id = await _enqueue_prediction_job(
            request=request,
            session=session,
            prediction_id=new_pred.id,
            user_id=user_id,
            relative_image_path=relative_image_path,
            location=location,
            lat=lat,
            lon=lon,
            language=language,
            plot_id=plot_id,
        )

        placeholder_result["prediction_id"] = new_pred.id
        placeholder_result["job_id"] = job_id
        return placeholder_result
    finally:
        await file.close()


@router.get("/predict/{prediction_id}", response_model=PredictionResponse)
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

    result = dict(prediction.result or {})
    result["prediction_id"] = prediction.id
    _apply_pipeline_status(result, prediction.status)

    # Traverse parent chain for historical images
    hist = []
    curr = prediction.parent
    while curr:
        curr_res = curr.result or {}
        old_image = curr_res.get("image", {})
        if old_image:
            hist.append({
                "id": curr.id,
                "created_at": curr.created_at.isoformat(),
                "disease": curr_res.get("disease", {}).get("label", "Unknown"),
                "severity_pct": curr_res.get("severity", {}).get("percent", 0.0),
                "severity_bucket": curr_res.get("severity", {}).get("bucket", "Unknown"),
                "raw_path": old_image.get("raw_path"),
                "processed_path": old_image.get("processed_path"),
            })
        curr = curr.parent

    # We want chronological order (oldest first)
    if hist:
        hist.reverse()
        result["historical_images"] = hist

    # Check for expert review
    if prediction.expert_review and prediction.status == "verified":
        result["expert_review_data"] = {
            "decision": prediction.expert_review.decision,
            "corrected_disease": prediction.expert_review.corrected_disease,
            "farmer_guidance": prediction.expert_review.farmer_guidance,
        }

    # Check for follow_ups
    if hasattr(prediction, "follow_ups") and prediction.follow_ups:
        latest_follow_up = prediction.follow_ups[-1]
        fu_res = dict(latest_follow_up.result or {})
        fu_res["prediction_id"] = latest_follow_up.id
        fu_res["status_string"] = latest_follow_up.status
        # Same normalisation as the parent so the client keeps polling a running rescan
        # and correctly detects a failed one.
        _apply_pipeline_status(fu_res, latest_follow_up.status)
        if latest_follow_up.expert_review and latest_follow_up.status == "verified":
            fu_res["expert_review_data"] = {
                "decision": latest_follow_up.expert_review.decision,
                "corrected_disease": latest_follow_up.expert_review.corrected_disease,
                "farmer_guidance": latest_follow_up.expert_review.farmer_guidance,
            }
        result["follow_up"] = fu_res

    return result


@router.post("/predictions/{prediction_id}/rescan", response_model=PredictionResponse)
@limiter.limit('20/minute')
async def rescan_prediction(
    request: Request,
    prediction_id: int,
    file: UploadFile = File(...),
    plot_id: int | None = Form(default=None),
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    # 1. Fetch existing prediction
    try:
        old_prediction = get_prediction(session, prediction_id, user_id)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    if old_prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found.")

    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        suffix = Path(file.filename or "upload.jpg").suffix.lower()
        if suffix in {".jpg", ".jpeg"}:
            file.content_type = "image/jpeg"
        elif suffix == ".png":
            file.content_type = "image/png"
        elif suffix == ".webp":
            file.content_type = "image/webp"
        else:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Upload a JPEG, PNG, or WebP image.",
            )

    # 2. Save new image
    suffix = Path(file.filename or "upload.jpg").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg" if file.content_type == "image/jpeg" else ".png"

    ensure_storage_directories()
    filename = f"{uuid.uuid4().hex}{suffix}"
    upload_path = _UPLOAD_DIR / filename
    relative_image_path = storage_relative_path(upload_path)

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

        old_res = dict(old_prediction.result or {})
        old_user = old_res.get("user", {}) or {}
        location = old_user.get("location", old_res.get("location", "Unknown"))
        lat = old_user.get("lat", 52.2297)
        lon = old_user.get("lon", 21.0122)
        language = old_user.get("language", old_res.get("language", "English"))

        context = create_context(
            image_path=str(upload_path),
            user_id=user_id,
            location=location,
            lat=lat,
            lon=lon,
            language=language,
        )

        # Fast synchronous image quality check
        from app.pipeline import _PREPROCESSOR

        context = _validate_preprocessing(context, upload_path, _PREPROCESSOR)

        placeholder_result = _placeholder_result(user_id, relative_image_path, suffix)

        new_pred = record_prediction(session, user_id, placeholder_result)
        if plot_id:
            new_pred.plot_id = plot_id
        new_pred.parent_id = old_prediction.id
        new_pred.plot_id = plot_id or old_prediction.plot_id
        new_pred.status = "processing"
        session.commit()

        job_id = await _enqueue_prediction_job(
            request=request,
            session=session,
            prediction_id=new_pred.id,
            user_id=user_id,
            relative_image_path=relative_image_path,
            location=location,
            lat=lat,
            lon=lon,
            language=language,
            is_rescan=True,
            parent_id=old_prediction.id,
            plot_id=new_pred.plot_id,
        )

        placeholder_result["prediction_id"] = new_pred.id
        placeholder_result["job_id"] = job_id
        return placeholder_result
    finally:
        await file.close()


@router.get("/job/{job_id}", response_model=dict)
@limiter.limit("20/minute")
async def get_job_status(request: Request, job_id: str):
    from arq.jobs import Job, JobStatus

    arq_pool = getattr(request.app.state, "arq_pool", None)
    if arq_pool is None:
        raise HTTPException(status_code=503, detail="Background job service is unavailable. Start Redis and retry.")

    # ArqRedis has no .job() helper; jobs are addressed through the Job class.
    job = Job(job_id, arq_pool)
    job_state = await job.status()
    if job_state == JobStatus.complete:
        return {"status": "complete"}
    if job_state == JobStatus.not_found:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": "processing", "state": job_state.value}


@router.post("/predictions/{prediction_id}/request-expert")
@limiter.limit('5/minute')
async def request_expert_review(
    request: Request,
    prediction_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    from app.models import Prediction

    pred = session.query(Prediction).filter(Prediction.id == prediction_id, Prediction.user_id == user_id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")

    if pred.expert_review and pred.expert_review.status in {"pending", "verified", "rejected"}:
        raise HTTPException(status_code=400, detail="Expert review already requested or completed")

    ensure_expert_review(session, pred, "Requested manually by farmer.")
    session.commit()

    return {"status": "Expert review requested successfully", "review_id": pred.expert_review.id}


# --------------------------------------------------------------------------------------
# live progress (WebSocket)
# --------------------------------------------------------------------------------------
_WS_DB_RECHECK_SECONDS = 3.0


def _progress_snapshot(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "crop": result.get("crop"),
        "disease": result.get("disease"),
        "pests": result.get("pests"),
        "severity": result.get("severity"),
    }


def _terminal_event(prediction: Any) -> dict[str, Any] | None:
    """Final event for a prediction that has already finished (or failed), else None."""
    result = prediction.result if isinstance(prediction.result, dict) else {}
    if prediction.status in _SUCCESS_STATUSES:
        return {
            "stage": "completed",
            "status": "completed",
            "message": "Diagnosis pipeline completed successfully.",
            "data": _progress_snapshot(result),
        }
    if prediction.status == "failed":
        err = result.get("error", "Processing failed")
        return {"stage": "failed", "status": "failed", "error": err, "message": err}
    return None


@router.websocket("/ws/predictions/{prediction_id}")
async def websocket_prediction_status(websocket: WebSocket, prediction_id: int):
    await websocket.accept()

    import redis.asyncio as aioredis

    from app.core.session import _session_factory
    from app.models import Prediction

    redis_url = urlparse(settings.REDIS_URL)
    redis_client = aioredis.Redis(
        host=redis_url.hostname or "127.0.0.1",
        port=redis_url.port or 6379,
        password=redis_url.password,
        db=int(redis_url.path.lstrip("/") or 0),
        decode_responses=True,
    )
    pubsub = redis_client.pubsub()
    channel = f"prediction_status:{prediction_id}"
    db = None

    def load_prediction():
        # expire_all() so we always see rows committed by the worker process.
        db.expire_all()
        return db.query(Prediction).filter(Prediction.id == prediction_id).first()

    try:
        # Subscribe BEFORE reading the DB snapshot so no event can fall in the gap between them.
        await pubsub.subscribe(channel)
        db = _session_factory()()

        existing = load_prediction()
        if existing is None:
            msg = "Prediction not found."
            await websocket.send_json({"stage": "failed", "status": "failed", "error": msg, "message": msg})
            return

        # Already finished (or failed) before the client connected: send the outcome and stop.
        terminal = _terminal_event(existing)
        if terminal is not None:
            await websocket.send_json(terminal)
            return

        # Mid-run connection: replay every stage that has already completed.
        existing_result = existing.result if isinstance(existing.result, dict) else {}
        snapshot_data = _progress_snapshot(existing_result)
        for stage_name, stage_info in (existing_result.get("stages") or {}).items():
            if isinstance(stage_info, dict) and stage_info.get("status") == "completed":
                await websocket.send_json({
                    "stage": stage_name,
                    "status": "completed",
                    "message": stage_info.get("message", ""),
                    "duration_ms": stage_info.get("duration_ms"),
                    "data": snapshot_data,
                })

        last_db_check = time.monotonic()
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                data = json.loads(message["data"])
                await websocket.send_json(data)
                if data.get("stage") in {"completed", "failed"} or data.get("status") == "failed":
                    break

            # Redis pub/sub is fire-and-forget: if an event was lost (or the worker died) the DB
            # is still the source of truth, so re-check it periodically.
            if time.monotonic() - last_db_check >= _WS_DB_RECHECK_SECONDS:
                last_db_check = time.monotonic()
                current = load_prediction()
                terminal = _terminal_event(current) if current is not None else None
                if terminal is not None:
                    await websocket.send_json(terminal)
                    break
    except WebSocketDisconnect:
        pass
    except Exception as e:
        _LOGGER.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        if db is not None:
            db.close()
        try:
            await pubsub.unsubscribe(channel)
            await pubsub.aclose()
        except Exception:
            pass
        try:
            await redis_client.aclose()
        except Exception:
            pass
        try:
            await websocket.close()
        except Exception:
            pass


# --------------------------------------------------------------------------------------
# Media Authorization Gateway & ARQ Job Status
# --------------------------------------------------------------------------------------
@router.get("/predictions/{prediction_id}/media-url/{media_type}")
async def get_prediction_media_url(
    prediction_id: int,
    media_type: str,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """
    Get a secure 15-minute authorized URL for prediction media (raw leaf, processed overlay, or audio).
    Strict Access Control:
    - Farmer owner: Allowed for own predictions.
    - Reviewing expert: Allowed if prediction has pending/verified expert review.
    - Admin: Allowed for all predictions.
    - Others: 403 Forbidden.
    """
    from app.models import Prediction, User
    from app.core.storage import get_storage

    caller = session.get(User, user_id)
    pred = session.get(Prediction, prediction_id)
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found.")

    is_owner = str(pred.user_id) == str(user_id)
    is_admin = caller and caller.role == "admin"
    is_reviewing_expert = (
        caller and caller.role in ["expert", "admin"] and (
            pred.status in ["pending_expert_review", "verified", "rescan_requested"]
            or pred.expert_review is not None
        )
    )

    if not (is_owner or is_admin or is_reviewing_expert):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission to access media for this prediction.",
        )

    norm_type = media_type.lower().strip()
    storage = get_storage()
    key: str | None = None
    if norm_type in ["raw", "image", "upload"]:
        key = pred.raw_path or (pred.image.raw_path if pred.image else None)
    elif norm_type in ["processed", "mask"]:
        key = pred.processed_path or (pred.image.processed_path if pred.image else None)
    elif norm_type in ["audio", "tts"]:
        res = pred.result if isinstance(pred.result, dict) else {}
        key = res.get("audio_path")
    else:
        raise HTTPException(status_code=422, detail="Invalid media_type. Allowed: raw, processed, audio.")

    if not key:
        raise HTTPException(status_code=404, detail=f"No {media_type} asset recorded for this prediction.")

    url = storage.get_url(key, expires_in=settings.S3_PRESIGNED_EXPIRY_SECONDS)
    return {
        "prediction_id": prediction_id,
        "media_type": norm_type,
        "url": url,
        "expires_in": settings.S3_PRESIGNED_EXPIRY_SECONDS,
    }


@router.get("/predictions/{prediction_id}/media/{media_type}")
async def get_prediction_media_stream(
    prediction_id: int,
    media_type: str,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Direct access stream or redirect to authorized presigned URL with ownership enforcement.
    """
    from app.models import Prediction, User
    from app.core.storage import get_storage
    from fastapi.responses import Response, RedirectResponse

    caller = session.get(User, user_id)
    pred = session.get(Prediction, prediction_id)
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found.")

    is_owner = str(pred.user_id) == str(user_id)
    is_admin = caller and caller.role == "admin"
    is_reviewing_expert = (
        caller and caller.role in ["expert", "admin"] and (
            pred.status in ["pending_expert_review", "verified", "rescan_requested"]
            or pred.expert_review is not None
        )
    )

    if not (is_owner or is_admin or is_reviewing_expert):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission to access media for this prediction.",
        )

    norm_type = media_type.lower().strip()
    storage = get_storage()
    key: str | None = None
    mime = "application/octet-stream"
    if norm_type in ["raw", "image", "upload"]:
        key = pred.raw_path or (pred.image.raw_path if pred.image else None)
        mime = "image/jpeg"
    elif norm_type in ["processed", "mask"]:
        key = pred.processed_path or (pred.image.processed_path if pred.image else None)
        mime = "image/jpeg"
    elif norm_type in ["audio", "tts"]:
        res = pred.result if isinstance(pred.result, dict) else {}
        key = res.get("audio_path")
        mime = "audio/mpeg"
    else:
        raise HTTPException(status_code=422, detail="Invalid media_type. Allowed: raw, processed, audio.")

    if not key:
        raise HTTPException(status_code=404, detail=f"No {media_type} asset found for this prediction.")

    if getattr(settings, "STORAGE_BACKEND", "local").lower() == "s3":
        presigned_url = storage.get_url(key, expires_in=settings.S3_PRESIGNED_EXPIRY_SECONDS)
        return RedirectResponse(url=presigned_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    try:
        content = storage.get(key)
        return Response(content=content, media_type=mime)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Media file not found.")


@router.get("/predictions/jobs/{job_id}")
async def get_prediction_job_status(
    job_id: str,
    request: Request,
    user_id: str = Depends(get_current_user),
) -> dict[str, Any]:
    """Retrieve ARQ worker queue status for a submitted job."""
    arq_pool = getattr(request.app.state, "arq_pool", None)
    if arq_pool is None:
        return {"job_id": job_id, "status": "unknown", "detail": "Worker pool unavailable."}
    from arq.jobs import Job
    job = Job(job_id=job_id, redis=arq_pool)
    try:
        job_status = await job.status()
        info = await job.info()
        return {
            "job_id": job_id,
            "status": str(job_status),
            "enqueue_time": info.enqueue_time.isoformat() if info and info.enqueue_time else None,
            "success": info.success if info else None,
        }
    except Exception as exc:
        return {"job_id": job_id, "status": "error", "detail": str(exc)}

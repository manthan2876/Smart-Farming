from __future__ import annotations

import uuid
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from app.core.limiter import limiter
from fastapi import Depends, File, Form, HTTPException, UploadFile, status, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core import get_session
from app.schemas import PredictionResponse, ErrorResponse
from app.context import create_context
from app.crud import record_prediction, get_prediction
from app.core.config import settings
from app.core.paths import ensure_storage_directories, storage_relative_path

router = APIRouter()

_UPLOAD_DIR = settings.UPLOAD_ROOT
_MAX_UPLOAD_BYTES = settings.UPLOAD_MAX_BYTES
_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
_LOGGER = logging.getLogger("smart-farming.api")



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
            
        import hashlib
        hash_val = hashlib.sha256(image_bytes).hexdigest()
        filename = f"{hash_val}{suffix}"
        upload_path = _UPLOAD_DIR / filename
        relative_image_path = storage_relative_path(upload_path)
        
        # Check cache
        from app.models import Image, Prediction
        existing_img = session.query(Image).filter(Image.raw_path == relative_image_path).first()
        if existing_img and existing_img.prediction:
            if existing_img.prediction.plot_id == plot_id:
                # Return instantly
                return {"job_id": None, "prediction_id": existing_img.prediction.id, "status": {"pipeline": "completed"}, "cached": True}
                
        with upload_path.open("wb") as destination:
            destination.write(image_bytes)
        
        # Create context
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
        context = _PREPROCESSOR.process(context)
        if context["status"]["preprocessing"] != "completed":
            if upload_path.exists():
                upload_path.unlink()
            raise HTTPException(
                status_code=400,
                detail="Image is too blurry or has poor lighting. Please retake the photo."
            )
            
        # Create placeholder prediction record
        placeholder_result = {
            "request_id": str(uuid.uuid4()),
            "user": {"id": user_id},
            "image": {"raw_path": relative_image_path, "processed_path": None, "resolution": None, "channels": None, "quality_score": 1.0, "format": suffix},
            "crop": {}, "disease": {}, "severity": {}, "pests": [], "pest_classification": {}, "weather": {}, "recommendation": {}, "notes": [],
            "status": {"preprocessing": "processing", "pipeline": "processing", "expert_review": "not_requested"}
        }
        
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
    if "status" not in result:
        result["status"] = {}
    if prediction.status in ("completed", "failed", "pending_expert_review"):
        result["status"]["pipeline"] = "completed"

    
    # Traverse parent chain for historical images
    hist = []
    curr = prediction.parent
    while curr:
        curr_res = curr.result
        old_image = curr_res.get("image", {})
        if old_image:
            hist.append({
                "id": curr.id,
                "created_at": curr.created_at.isoformat(),
                "disease": curr_res.get("disease", {}).get("label", "Unknown"),
                "severity_pct": curr_res.get("severity", {}).get("percent", 0.0),
                "severity_bucket": curr_res.get("severity", {}).get("bucket", "Unknown"),
                "raw_path": old_image.get("raw_path"),
                "processed_path": old_image.get("processed_path")
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
        fu_res = dict(latest_follow_up.result)
        fu_res["prediction_id"] = latest_follow_up.id
        fu_res["status_string"] = latest_follow_up.status
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
    from app.models import Prediction, ExpertReview
    
    # 1. Fetch existing prediction
    try:
        old_prediction = get_prediction(session, prediction_id, user_id)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    if old_prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found.")

    if file.content_type not in _ALLOWED_CONTENT_TYPES:
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

        old_res = dict(old_prediction.result)
        old_user = old_res.get("user", {})
        location = old_user.get("location", old_res.get("location", "Unknown"))
        lat = old_user.get("lat", 52.2297)
        lon = old_user.get("lon", 21.0122)
        language = old_user.get("language", old_res.get("language", "English"))
        
        context = create_context(
            image_path=str(upload_path),
            user_id=user_id,
            location=location,
            lat=52.2297,
            lon=21.0122,
            language=language,
        )
        
        # Fast synchronous image quality check
        from app.pipeline import _PREPROCESSOR
        context = _PREPROCESSOR.process(context)
        if context["status"]["preprocessing"] != "completed":
            if upload_path.exists():
                upload_path.unlink()
            raise HTTPException(
                status_code=400,
                detail="Image is too blurry or has poor lighting. Please retake the photo."
            )
            
        # Create placeholder prediction record
        placeholder_result = {
            "request_id": str(uuid.uuid4()),
            "user": {"id": user_id},
            "image": {"raw_path": relative_image_path, "processed_path": None, "resolution": None, "channels": None, "quality_score": 1.0, "format": suffix},
            "crop": {}, "disease": {}, "severity": {}, "pests": [], "pest_classification": {}, "weather": {}, "recommendation": {}, "notes": [],
            "status": {"preprocessing": "processing", "pipeline": "processing", "expert_review": "not_requested"}
        }
        
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
    arq_pool = getattr(request.app.state, "arq_pool", None)
    if arq_pool is None:
        raise HTTPException(status_code=503, detail="Background job service is unavailable. Start Redis and retry.")

    job = arq_pool.job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    status = await job.status()
    import arq.jobs
    if status == arq.jobs.JobStatus.complete:
        return {"status": "complete"}
    elif status == arq.jobs.JobStatus.not_found:
        raise HTTPException(status_code=404, detail="Job not found")
    else:
        return {"status": "processing"}

@router.post("/predictions/{prediction_id}/request-expert")
@limiter.limit('5/minute')
async def request_expert_review(
    request: Request,
    prediction_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    from app.models import Prediction
    pred = session.query(Prediction).filter(Prediction.id == prediction_id, Prediction.user_id == user_id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")
        
    res = dict(pred.result)
    status_block = res.get("status", {})
    if status_block.get("expert_review") in ["pending", "completed"]:
        raise HTTPException(status_code=400, detail="Expert review already requested or completed")
        
    status_block["expert_review"] = "pending"
    status_block["expert_reason"] = "Requested manually by farmer"
    res["status"] = status_block
    
    pred.result = res
    pred.status = "pending_expert_review"
    session.commit()
    
    return {"status": "Expert review requested successfully"}

from fastapi import WebSocket, WebSocketDisconnect
import asyncio

@router.websocket("/ws/predictions/{prediction_id}")
async def websocket_prediction_status(websocket: WebSocket, prediction_id: int):
    await websocket.accept()
    import redis.asyncio as aioredis
    import json
    
    from urllib.parse import urlparse
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
    await pubsub.subscribe(channel)
    
    from app.core.session import _session_factory
    from app.models import Prediction
    db = _session_factory()()
    
    try:
        # Also send the current status from DB immediately just in case it's already done or we missed an event
        existing = db.query(Prediction).filter(Prediction.id == prediction_id).first()
        if existing and existing.status == "completed":
            await websocket.send_json({"stage": "completed"})
            return
            
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                data = json.loads(message["data"])
                await websocket.send_json(data)
                if data.get("stage") == "completed":
                    break
            # heartbeat or yield
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        _LOGGER.error(f"WebSocket error: {e}")
    finally:
        db.close()
        await pubsub.unsubscribe(channel)
        await redis_client.aclose()

from __future__ import annotations

import uuid
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from app.core.limiter import limiter
from fastapi import Depends, File, Form, HTTPException, UploadFile, status, BackgroundTasks, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core import get_session
from app.utils.json_utils import _json_safe
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



def run_background_pipeline(
    prediction_id: int, 
    user_id: str,
    context: dict,
    relative_image_path: str,
    is_rescan: bool = False,
    parent_id: int | None = None
):
    from app.core.session import _session_factory
    from app.models import Prediction, ExpertReview
    import logging
    _BG_LOGGER = logging.getLogger("smart-farming.background")
    
    db = _session_factory()()
    try:
        # Run heavy pipeline incrementally
        from app.pipeline import (
            _PREPROCESSOR, predict_crop, route_to_disease_model, 
            predict_disease, estimate_severity, predict_pest, 
            fetch_weather, generate_recommendation, _CONFIG
        )
        from app.api.endpoints.predict import _public_result
        import time
        
        # Execute pipeline in memory without saving partial results to the database
        # (Preprocessing was already successfully completed synchronously)
        
        if context["status"]["preprocessing"] == "completed":
            # Step 2: Crop
            context = predict_crop(context, _CONFIG)
            context["status"]["crop_identification"] = "completed"

            # Step 3: Disease
            context = route_to_disease_model(context, _CONFIG)
            context = predict_disease(context, _CONFIG)
            context = estimate_severity(context)
            context["status"]["disease_classification"] = "completed"

            # Step 4: Pest & Weather
            context = predict_pest(context, _CONFIG)
            context = fetch_weather(context, _CONFIG)
            context["status"]["pest_detection"] = "completed"

            # Step 5: Advisory
            context = generate_recommendation(context, _CONFIG)

        result = context
        preprocessing_status = result.get("status", {}).get("preprocessing")
        if preprocessing_status != "completed":
            new_status = "failed"
            public_result = {"error": "Image quality check failed; please upload a clearer leaf image."}
        else:
            if "image" in result and isinstance(result["image"], dict):
                result["image"]["raw_path"] = relative_image_path
            
            public_result = _public_result(result)
            
            # Determine status via comprehensive rules
            d_conf = public_result.get("disease", {}).get("confidence", 0.0) or 0.0
            c_conf = public_result.get("crop", {}).get("confidence", 0.0) or 0.0
            sev_pct = public_result.get("severity", {}).get("percent", 0.0) or 0.0
            pests = public_result.get("pests", [])
            img_qual = public_result.get("image", {}).get("quality_score", 1.0) or 1.0
            all_probs = public_result.get("disease", {}).get("all_probs", {})
            advisory = public_result.get("recommendation", {})
            
            new_status = "ready"
            res_status = dict(public_result.get("status", {}))
            res_status["expert_review"] = "not_requested"
            res_status["pipeline"] = "completed"
            
            public_result["status"] = res_status
            
        # Update Database Record
        pred = db.query(Prediction).filter(Prediction.id == prediction_id).first()
        if pred:
            # Merge context user data
            if not public_result.get("error"):
                public_result["user"] = {"id": user_id}
            
            pred.result = public_result
            pred.status = new_status
            
            if hasattr(pred, "image_path"):
                pred.image_path = relative_image_path
                
            if new_status == "pending_expert_review":
                if not pred.expert_review:
                    pred.expert_review = ExpertReview(status="pending")
                
            db.commit()
    except Exception as e:
        _BG_LOGGER.error(f"Background ML Pipeline failed: {e}")
        db.rollback()
        pred = db.query(Prediction).filter(Prediction.id == prediction_id).first()
        if pred:
            pred.status = "failed"
            pred.result = {"error": str(e)}
            db.commit()
    finally:
        db.close()

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
@limiter.limit('20/minute')
async def predict(
    request: Request,
    background_tasks: BackgroundTasks,
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
    
    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{suffix}"
    upload_path = _UPLOAD_DIR / filename
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
        
        # Dispatch background task
        background_tasks.add_task(
            run_background_pipeline,
            prediction_id=new_pred.id,
            user_id=user_id,
            context=context,
            relative_image_path=relative_image_path
        )
        
        placeholder_result["prediction_id"] = new_pred.id
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
    background_tasks: BackgroundTasks,
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
    
    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{suffix}"
    upload_path = _UPLOAD_DIR / filename
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

        old_res = dict(old_prediction.result)
        location = old_res.get("location", "Unknown")
        language = old_res.get("language", "English")
        
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
        
        # Dispatch background task
        background_tasks.add_task(
            run_background_pipeline,
            prediction_id=new_pred.id,
            user_id=user_id,
            context=context,
            relative_image_path=relative_image_path
        )
        
        placeholder_result["prediction_id"] = new_pred.id
        return placeholder_result
    finally:
        await file.close()

@router.get("/job/{job_id}", response_model=dict)
@limiter.limit("20/minute")
async def get_job_status(request: Request, job_id: str):
    job = request.app.state.arq_pool.job(job_id)
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

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
    BackgroundTasks,
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


def _enrich_image_urls(result: dict) -> dict:
    """If S3 storage is enabled, generate fresh presigned S3 URLs for raw and processed images."""
    if getattr(settings, "STORAGE_BACKEND", "local").lower() in ("s3", "gcs"):
        try:
            from app.core.storage import get_storage
            storage = get_storage()
            img = result.get("image")
            if isinstance(img, dict):
                raw_k = img.get("raw_path")
                proc_k = img.get("processed_path")
                if raw_k:
                    img["raw_url"] = storage.get_url(raw_k, expires_in=settings.S3_PRESIGNED_EXPIRY_SECONDS)
                if proc_k:
                    img["processed_url"] = storage.get_url(proc_k, expires_in=settings.S3_PRESIGNED_EXPIRY_SECONDS)
        except Exception as exc:
            _LOGGER.warning("Could not generate presigned S3 URLs: %s", exc)
    return result


def _ensure_processed_image_for_prediction(prediction, result: dict, session: Session) -> None:
    """Self-healing helper: if an existing prediction has a raw image but is missing its
    processed heatmap (e.g. historical scan), generate it on-the-fly and persist to S3."""
    img = result.setdefault("image", {})
    proc_path = img.get("processed_path") or prediction.processed_path
    raw_path = img.get("raw_path") or prediction.raw_path

    if proc_path:
        img["processed_path"] = proc_path
        return

    if not raw_path:
        return

    try:
        from pathlib import Path
        import base64
        from app.core.storage import get_storage
        from app.services.model_client import call_model_service_sync
        from app.core.config import settings

        storage = get_storage()
        clean_name = Path(raw_path).name
        raw_obj = Path(raw_path)
        if raw_obj.exists():
            raw_bytes = raw_obj.read_bytes()
        elif storage.exists(raw_path):
            raw_bytes = storage.get(raw_path)
        else:
            return

        cv_res = call_model_service_sync(raw_bytes, clean_name)
        b64_str = cv_res.get("image", {}).get("processed_image_base64")
        if b64_str:
            proc_bytes = base64.b64decode(b64_str)
            storage.save(proc_bytes, f"processed/{clean_name}", content_type="image/jpeg")
            local_p = settings.DATA_ROOT / "processed" / clean_name
            local_p.parent.mkdir(parents=True, exist_ok=True)
            local_p.write_bytes(proc_bytes)

            rel_proc = f"data/processed/{clean_name}"
            img["processed_path"] = rel_proc
            prediction.processed_path = rel_proc
            prediction.result = result
            session.commit()
    except Exception as exc:
        _LOGGER.warning("Could not auto-generate missing processed image for prediction %s: %s", prediction.id, exc)



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


async def _validate_preprocessing_remote(
    image_bytes: bytes, filename: str, content_type: str = "image/jpeg"
) -> None:
    from app.services.model_client import call_model_service
    await call_model_service(image_bytes, filename, content_type)


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
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    location: str = Form(default="Unknown"),
    lat: float | None = Form(default=None),
    lon: float | None = Form(default=None),
    language: str = Form(default="English"),
    plot_id: int | None = Form(default=None),
    client_uuid: str | None = Form(default=None),
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

        # 1. Fast Upstash Redis REST deduplication check (sub-20ms)
        try:
            from app.core.redis_rest import redis_rest
            if client_uuid:
                cached_uuid_res = await redis_rest.get(f"sf:uuid:{client_uuid}")
                if cached_uuid_res and isinstance(cached_uuid_res, dict):
                    cached_uuid_res["cached"] = True
                    return cached_uuid_res

            cached_dedup = await redis_rest.get(f"sf:dedup:{hash_val}")
            if cached_dedup and isinstance(cached_dedup, dict) and cached_dedup.get("status", {}).get("pipeline") in _SUCCESS_STATUSES:
                cached_dedup["cached"] = True
                return cached_dedup
        except Exception:
            pass

        # Resolve coordinates if not provided: Plot -> User farm -> Indian regional default
        if lat is None or lon is None:
            if plot_id:
                from app.models import Plot
                plot_obj = session.get(Plot, plot_id)
                if plot_obj and plot_obj.user_id == user_id:
                    if plot_obj.latitude is not None and plot_obj.longitude is not None:
                        lat = float(plot_obj.latitude)
                        lon = float(plot_obj.longitude)
                    elif plot_obj.farm and plot_obj.farm.latitude is not None and plot_obj.farm.longitude is not None:
                        lat = float(plot_obj.farm.latitude)
                        lon = float(plot_obj.farm.longitude)
                        if location == "Unknown" and plot_obj.farm.location:
                            location = plot_obj.farm.location

            if lat is None or lon is None:
                from app.models import User
                user_obj = session.get(User, user_id)
                if user_obj and user_obj.farm:
                    if user_obj.farm.latitude is not None and user_obj.farm.longitude is not None:
                        lat = float(user_obj.farm.latitude)
                        lon = float(user_obj.farm.longitude)
                    if location == "Unknown" and user_obj.farm.location:
                        location = user_obj.farm.location

            if lat is None or lon is None:
                lat = getattr(settings, "DEFAULT_LAT", 21.7645)
                lon = getattr(settings, "DEFAULT_LON", 72.1519)
                if location == "Unknown":
                    location = getattr(settings, "DEFAULT_LOCATION", "Gujarat, India")

        # Save to active storage backend (Local disk or AWS S3 / GCS)
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

        # Enrich farm and plot context
        farm_info = {}
        plot_info = {}
        if plot_id:
            from app.models import Plot, Farm
            plot_obj = session.get(Plot, plot_id)
            if plot_obj:
                plot_info = {
                    "id": plot_obj.id,
                    "name": plot_obj.name,
                    "crop": plot_obj.crop,
                    "area_acres": plot_obj.area_acres,
                    "status": plot_obj.status,
                }
                if plot_obj.farm:
                    farm_info = {
                        "id": plot_obj.farm.id,
                        "name": plot_obj.farm.name,
                        "location": plot_obj.farm.location,
                        "area_acres": plot_obj.farm.area_acres,
                        "crop_history": plot_obj.farm.crop_history or [],
                    }
        if not farm_info:
            from app.models import Farm
            farm_obj = session.query(Farm).filter(Farm.user_id == user_id).first()
            if farm_obj:
                farm_info = {
                    "id": farm_obj.id,
                    "name": farm_obj.name,
                    "location": farm_obj.location,
                    "area_acres": farm_obj.area_acres,
                    "crop_history": farm_obj.crop_history or [],
                }

        context = create_context(
            image_path=relative_image_path,
            user_id=user_id,
            location=location,
            lat=lat,
            lon=lon,
            language=language,
            farm=farm_info,
            plot=plot_info,
        )

        # If Redis/ARQ is not configured or offline, execute synchronously via Server 2
        arq_pool = getattr(request.app.state, "arq_pool", None)
        if arq_pool is None or not getattr(settings, "REQUIRE_REDIS", False):
            from app.pipeline import run_pipeline

            context = await run_pipeline(
                context, image_bytes, filename, file.content_type or "image/jpeg"
            )

            # Ensure relative storage path is preserved for asset serving
            context["image"]["raw_path"] = relative_image_path

            public_res = _public_result(context)
            if plot_info:
                public_res["plot"] = plot_info
            if farm_info:
                public_res["farm"] = farm_info

            new_pred = record_prediction(session, user_id, public_res)
            if plot_id:
                new_pred.plot_id = plot_id

            # Check confidence and near-tie for expert review escalation
            disease_thresh = getattr(settings, "DISEASE_CONFIDENCE_THRESHOLD", 0.7)
            crop_thresh = getattr(settings, "CROP_CONFIDENCE_THRESHOLD", 0.7)
            disease_conf = public_res.get("disease", {}).get("confidence") or 0.0
            crop_conf = public_res.get("crop", {}).get("confidence") or 0.0
            is_near_tie = public_res.get("disease", {}).get("is_near_tie", False)

            is_unsupported_crop = (
                public_res.get("crop", {}).get("status") == "unsupported_crop"
                or public_res.get("status", {}).get("decision_routing") == "unsupported_crop"
                or crop_conf < crop_thresh
            )

            review_reason: str | None = None
            if is_unsupported_crop:
                crop_name = public_res.get("crop", {}).get("label") or "Unknown Crop"
                review_reason = (
                    f"Crop '{crop_name}' is unsupported or identified with low confidence ({crop_conf * 100:.1f}%). "
                    "Automated disease models support Cotton, Groundnut, Pepper Bell, Potato, and Tomato."
                )
                public_res.setdefault("status", {})["mask_advisory"] = True
            elif is_near_tie:
                could_also_be_data = public_res.get("disease", {}).get("could_also_be", {})
                lbl = could_also_be_data.get("label", "alternative candidate") if isinstance(could_also_be_data, dict) else "alternative candidate"
                review_reason = f"Near-tie diagnosis with alternative candidate '{lbl}'. Flagged for expert verification."
            elif disease_conf < disease_thresh:
                review_reason = "Disease confidence is below configured threshold."

            if review_reason:
                ensure_expert_review(session, new_pred, review_reason)
                new_pred.status = "pending_expert_review"
                public_res.setdefault("status", {})["expert_review"] = "pending"
                public_res.setdefault("status", {})["pipeline"] = "completed"
            else:
                new_pred.status = "completed"
                public_res.setdefault("status", {})["pipeline"] = "completed"

            session.commit()

            public_res["prediction_id"] = new_pred.id
            public_res["job_id"] = None
            final_res = _enrich_image_urls(public_res)

            # Save in Upstash Redis REST dedup cache (24h TTL)
            try:
                from app.core.redis_rest import redis_rest
                await redis_rest.set(f"sf:dedup:{hash_val}", final_res, ex=86400)
                if client_uuid:
                    await redis_rest.set(f"sf:uuid:{client_uuid}", final_res, ex=86400)
            except Exception:
                pass

            # Pre-translate Hindi & Gujarati in background thread without blocking farmer
            canonical_rec = context.get("recommendation", {})
            if canonical_rec and isinstance(canonical_rec, dict):
                rec_fields = {k: v.strip() for k, v in canonical_rec.items() if isinstance(v, str) and v.strip()}
                if rec_fields:
                    from app.core.arq import enqueue_translation
                    background_tasks.add_task(
                        enqueue_translation,
                        "prediction",
                        new_pred.id,
                        rec_fields,
                    )

            return final_res

        # Fast synchronous image quality check via model service before enqueuing
        await _validate_preprocessing_remote(image_bytes, file.filename or filename, file.content_type or "image/jpeg")

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
    request: Request,
    prediction_id: int,
    lang: str | None = None,
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

    # Automatically mark unread alerts for this prediction as read
    try:
        from app.models import Alert
        unread_alerts = session.query(Alert).filter(
            Alert.prediction_id == prediction.id,
            Alert.user_id == user_id,
            Alert.is_read == False,
        ).all()
        if unread_alerts:
            for alert_obj in unread_alerts:
                alert_obj.is_read = True
            session.commit()
    except Exception as exc:
        session.rollback()
        _LOGGER.warning("Could not auto-mark alerts as read for prediction %s: %s", prediction_id, exc)

    _ensure_processed_image_for_prediction(prediction, result, session)
    if prediction.processed_path and not result.get("image", {}).get("processed_path"):
        result.setdefault("image", {})["processed_path"] = prediction.processed_path
    if prediction.raw_path and not result.get("image", {}).get("raw_path"):
        result.setdefault("image", {})["raw_path"] = prediction.raw_path

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

    # Attach plot and farm if present
    if getattr(prediction, "plot", None):
        result.setdefault("plot", {
            "id": prediction.plot.id,
            "name": prediction.plot.name,
            "crop_type": getattr(prediction.plot, "crop", None),
            "area_acres": prediction.plot.area_acres,
        })
        if getattr(prediction.plot, "farm", None):
            result.setdefault("farm", {
                "id": prediction.plot.farm.id,
                "name": prediction.plot.farm.name,
                "total_area_acres": getattr(prediction.plot.farm, "area_acres", None),
            })
    elif getattr(prediction, "plot_id", None) and not result.get("plot"):
        try:
            from app.models.plot import Plot
            p_obj = session.get(Plot, prediction.plot_id)
            if p_obj:
                result["plot"] = {
                    "id": p_obj.id,
                    "name": p_obj.name,
                    "crop_type": getattr(p_obj, "crop", None),
                    "area_acres": p_obj.area_acres,
                }
                if getattr(p_obj, "farm", None):
                    result["farm"] = {
                        "id": p_obj.farm.id,
                        "name": p_obj.farm.name,
                        "total_area_acres": getattr(p_obj.farm, "area_acres", None),
                    }
        except Exception:
            pass

    # Attach treatment progress if this is a follow-up rescan
    if prediction.parent and not result.get("treatment_progress"):
        try:
            from app.services.prediction_job import calculate_treatment_progress
            current_dis = result.get("disease", {}).get("label", "Unknown")
            current_sev = float(result.get("severity", {}).get("percent", 0.0) or 0.0)
            current_bkt = result.get("severity", {}).get("bucket", "Unknown")
            result["treatment_progress"] = calculate_treatment_progress(
                prediction.parent,
                current_dis,
                current_sev,
                current_bkt,
            )
        except Exception as exc:
            _LOGGER.warning("Failed to calculate treatment progress in prediction_detail: %s", exc)

    # Check for expert review
    if prediction.expert_review:
        result["expert_review_data"] = {
            "decision": prediction.expert_review.decision,
            "corrected_disease": prediction.expert_review.corrected_disease,
            "corrected_severity": prediction.expert_review.corrected_severity,
            "farmer_guidance": prediction.expert_review.farmer_guidance,
            "status": prediction.expert_review.status,
        }
        if prediction.expert_review.status == "verified" or prediction.status == "verified":
            result.setdefault("status", {})["expert_review"] = "verified"
            if prediction.expert_review.corrected_disease:
                result.setdefault("disease", {})["label"] = prediction.expert_review.corrected_disease
            if prediction.expert_review.corrected_severity is not None:
                result.setdefault("severity", {})["percent"] = prediction.expert_review.corrected_severity

    # Check for follow_ups
    if hasattr(prediction, "follow_ups") and prediction.follow_ups:
        latest_follow_up = prediction.follow_ups[-1]
        fu_res = dict(latest_follow_up.result or {})
        fu_res["prediction_id"] = latest_follow_up.id
        fu_res["status_string"] = latest_follow_up.status
        # Same normalisation as the parent so the client keeps polling a running rescan
        # and correctly detects a failed one.
        _apply_pipeline_status(fu_res, latest_follow_up.status)
        _enrich_image_urls(fu_res)
        if not fu_res.get("treatment_progress"):
            try:
                from app.services.prediction_job import calculate_treatment_progress
                fu_dis = fu_res.get("disease", {}).get("label", "Unknown")
                fu_sev = float(fu_res.get("severity", {}).get("percent", 0.0) or 0.0)
                fu_bkt = fu_res.get("severity", {}).get("bucket", "Unknown")
                fu_res["treatment_progress"] = calculate_treatment_progress(
                    prediction,
                    fu_dis,
                    fu_sev,
                    fu_bkt,
                )
            except Exception:
                pass
        if latest_follow_up.expert_review and latest_follow_up.status == "verified":
            fu_res["expert_review_data"] = {
                "decision": latest_follow_up.expert_review.decision,
                "corrected_disease": latest_follow_up.expert_review.corrected_disease,
                "farmer_guidance": latest_follow_up.expert_review.farmer_guidance,
            }
        result["follow_up"] = fu_res

    # Overlay pre-computed translations from entity_translations table (instant lookup)
    from app.models.translation import EntityTranslation
    translations = dict(result.get("translations") or {})
    try:
        cached_trans = session.query(EntityTranslation).filter_by(
            entity_type="prediction",
            entity_id=str(prediction_id),
            status="done"
        ).all()
        for ct in cached_trans:
            if ct.language not in translations:
                translations[ct.language] = dict(result.get("recommendation") or {})
                translations[ct.language]["language"] = ct.language
            translations[ct.language][ct.field_name] = ct.translated_text
        result["translations"] = translations
    except Exception:
        pass

    req_lang = lang or request.headers.get("accept-language")
    if req_lang and not req_lang.lower().startswith("en"):
        norm_code = "gu" if req_lang.lower().startswith("gu") else ("hi" if req_lang.lower().startswith("hi") else None)
        if norm_code:
            if norm_code in translations and translations[norm_code]:
                result["recommendation"] = dict(translations[norm_code])
            if prediction.expert_review and result.get("expert_review_data"):
                try:
                    guidance_trans = session.query(EntityTranslation).filter_by(
                        entity_type="expert_review",
                        entity_id=str(prediction.expert_review.id),
                        field_name="farmer_guidance",
                        language=norm_code,
                        status="done",
                    ).first()
                    if guidance_trans and guidance_trans.translated_text:
                        result["expert_review_data"]["farmer_guidance"] = guidance_trans.translated_text
                except Exception:
                    pass

    return _enrich_image_urls(result)


@router.post("/predictions/{prediction_id}/rescan", response_model=PredictionResponse)
@limiter.limit('20/minute')
async def rescan_prediction(
    request: Request,
    background_tasks: BackgroundTasks,
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
        lat = old_user.get("lat") or getattr(settings, "DEFAULT_LAT", 21.7645)
        # Enrich farm and plot context
        effective_plot_id = plot_id or old_prediction.plot_id
        farm_info = {}
        plot_info = {}
        if effective_plot_id:
            from app.models import Plot, Farm
            plot_obj = session.get(Plot, effective_plot_id)
            if plot_obj:
                plot_info = {
                    "id": plot_obj.id,
                    "name": plot_obj.name,
                    "crop": plot_obj.crop,
                    "area_acres": plot_obj.area_acres,
                    "status": plot_obj.status,
                }
                if plot_obj.farm:
                    farm_info = {
                        "id": plot_obj.farm.id,
                        "name": plot_obj.farm.name,
                        "location": plot_obj.farm.location,
                        "area_acres": plot_obj.farm.area_acres,
                        "crop_history": plot_obj.farm.crop_history or [],
                    }
        if not farm_info:
            from app.models import Farm
            farm_obj = session.query(Farm).filter(Farm.user_id == user_id).first()
            if farm_obj:
                farm_info = {
                    "id": farm_obj.id,
                    "name": farm_obj.name,
                    "location": farm_obj.location,
                    "area_acres": farm_obj.area_acres,
                    "crop_history": farm_obj.crop_history or [],
                }

        context = create_context(
            image_path=relative_image_path,
            user_id=user_id,
            location=location,
            lat=lat,
            lon=lon,
            language=language,
            farm=farm_info,
            plot=plot_info,
        )

        image_bytes = upload_path.read_bytes()

        # If Redis/ARQ is not configured or offline, execute synchronously via Server 2
        arq_pool = getattr(request.app.state, "arq_pool", None)
        if arq_pool is None or not getattr(settings, "REQUIRE_REDIS", False):
            from app.pipeline import run_pipeline

            context = await run_pipeline(
                context, image_bytes, filename, file.content_type or "image/jpeg"
            )
            context["image"]["raw_path"] = relative_image_path

            public_res = _public_result(context)

            from app.services.prediction_job import calculate_treatment_progress, _as_float
            cur_disease = public_res.get("disease", {}).get("label") or "Unknown"
            cur_sev = _as_float(public_res.get("severity", {}).get("percent")) or 0.0
            cur_bucket = public_res.get("severity", {}).get("bucket") or "Unknown"
            public_res["treatment_progress"] = calculate_treatment_progress(old_prediction, cur_disease, cur_sev, cur_bucket)
            if plot_info:
                public_res["plot"] = plot_info
            if farm_info:
                public_res["farm"] = farm_info

            new_pred = record_prediction(session, user_id, public_res)
            new_pred.parent_id = old_prediction.id
            new_pred.plot_id = effective_plot_id
            new_pred.status = "completed"
            session.commit()

            public_res["prediction_id"] = new_pred.id
            public_res["job_id"] = None
            final_res = _enrich_image_urls(public_res)

            # Pre-translate Hindi & Gujarati in background thread without blocking farmer
            canonical_rec = context.get("recommendation", {})
            if canonical_rec and isinstance(canonical_rec, dict):
                rec_fields = {k: v.strip() for k, v in canonical_rec.items() if isinstance(v, str) and v.strip()}
                if rec_fields:
                    from app.core.arq import enqueue_translation
                    background_tasks.add_task(
                        enqueue_translation,
                        "prediction",
                        new_pred.id,
                        rec_fields,
                    )

            return final_res

        # Fast synchronous image quality check via model service before enqueuing
        await _validate_preprocessing_remote(image_bytes, file.filename or filename, file.content_type or "image/jpeg")

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

    import asyncio
    from app.core.events import prediction_hub
    from app.core.session import _session_factory
    from app.models import Prediction

    db = None

    def load_prediction():
        # expire_all() so we always see rows committed by the worker process.
        db.expire_all()
        return db.query(Prediction).filter(Prediction.id == prediction_id).first()

    try:
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
        hub_stream = prediction_hub.subscribe(prediction_id)

        while True:
            try:
                # Wait for the next in-memory broadcast (< 1ms when emitted)
                event = await asyncio.wait_for(hub_stream.__anext__(), timeout=1.0)
                await websocket.send_json(event)
                if event.get("stage") in {"completed", "failed"} or event.get("status") == "failed":
                    break
            except asyncio.TimeoutError:
                pass

            # Fallback DB check in case an event was committed without a live broadcaster
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

    if getattr(settings, "STORAGE_BACKEND", "local").lower() in ("s3", "gcs"):
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

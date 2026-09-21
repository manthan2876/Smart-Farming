from __future__ import annotations

import json
import logging
from urllib.parse import urlparse

import redis

from app.context import create_context
from app.core.config import settings
from app.core.paths import resolve_storage_path
from app.core.session import _session_factory
from app.crud.expert_review import ensure_expert_review
from app.models import ExpertReview, Prediction
from app.pipeline import (
    _CONFIG,
    _PREPROCESSOR,
    estimate_severity,
    fetch_weather,
    generate_recommendation,
    predict_crop,
    predict_disease,
    predict_pest,
    route_to_disease_model,
)
from app.utils.json_utils import _json_safe

logger = logging.getLogger("smart-farming.background")


def _public_result(context: dict) -> dict:
    public_context = {key: value for key, value in context.items() if not key.startswith("_")}
    public_context["image"] = {
        key: value
        for key, value in public_context.get("image", {}).items()
        if key != "leaf_crop"
    }
    return _json_safe(public_context)


def _redis_client() -> redis.Redis:
    redis_url = urlparse(settings.REDIS_URL)
    return redis.Redis(
        host=redis_url.hostname or "127.0.0.1",
        port=redis_url.port or 6379,
        password=redis_url.password,
        db=int(redis_url.path.lstrip("/") or 0),
        decode_responses=True,
    )


from datetime import datetime, timezone
import time

def run_prediction_job(
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
) -> None:
    db = _session_factory()()
    redis_client = _redis_client()
    job_start_time = time.perf_counter()
    current_stage = "initialization"
    current_stage_t0 = time.perf_counter()

    def push_status(stage: str, status: str = "completed", message: str = "", duration_ms: int | None = None) -> None:
        payload = {
            "stage": stage,
            "status": status,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if duration_ms is not None:
            payload["duration_ms"] = duration_ms
        try:
            redis_client.publish(
                f"prediction_status:{prediction_id}",
                json.dumps(payload),
            )
        except Exception:
            logger.debug("Unable to publish prediction status", exc_info=True)

    try:
        prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
        if prediction is None:
            raise ValueError(f"Prediction {prediction_id} was not found")
        if prediction.status not in {"processing", "failed"}:
            return

        raw_path = resolve_storage_path(relative_image_path)
        if not raw_path.exists():
            raise FileNotFoundError(f"Prediction image not found: {relative_image_path}")

        context = create_context(
            image_path=str(raw_path),
            user_id=user_id,
            location=location,
            lat=lat,
            lon=lon,
            language=language,
        )
        prediction.status = "processing"
        db.commit()

        def stage_start(stage_name: str, message: str = "") -> float:
            nonlocal current_stage, current_stage_t0
            current_stage = stage_name
            current_stage_t0 = time.perf_counter()
            now_iso = datetime.now(timezone.utc).isoformat()
            if "status" not in context:
                context["status"] = {}
            if "stages" not in context:
                context["stages"] = {}
            context["status"][stage_name] = "processing"
            context["stages"][stage_name] = {
                "status": "processing",
                "message": message,
                "started_at": now_iso,
                "completed_at": None,
                "duration_ms": None,
            }
            push_status(stage_name, "processing", message)
            return current_stage_t0

        def stage_finish(stage_name: str, t0: float, message: str = "", extra_events: list[str] | None = None) -> int:
            duration_ms = round((time.perf_counter() - t0) * 1000)
            now_iso = datetime.now(timezone.utc).isoformat()
            context["status"][stage_name] = "completed"
            if stage_name not in context["stages"]:
                context["stages"][stage_name] = {}
            context["stages"][stage_name].update({
                "status": "completed",
                "message": message,
                "completed_at": now_iso,
                "duration_ms": duration_ms,
            })
            push_status(stage_name, "completed", message, duration_ms)
            if extra_events:
                for extra_stage in extra_events:
                    push_status(extra_stage, "completed", message, duration_ms)
            return duration_ms

        # 1. Preprocessing
        t0 = stage_start("preprocessing", "Validating image quality and clarity...")
        context = _PREPROCESSOR.process(context)
        prep_status = context.get("status", {}).get("preprocessing")
        if prep_status != "completed":
            if prep_status == "failed_blur":
                blur_score = context.get("image", {}).get("blur_score", 0.0)
                err = (
                    f"Image is too blurry (sharpness score: {blur_score:.1f}, "
                    f"required: >= {_PREPROCESSOR.blur_threshold:.1f}). Please hold the camera steady and refocus on the leaf."
                )
            elif prep_status == "failed_lighting":
                brightness = context.get("image", {}).get("brightness_score", 0.0)
                err = (
                    f"Image lighting is outside acceptable range (brightness: {brightness:.1f}, "
                    f"expected between {_PREPROCESSOR.min_brightness:.1f} and {_PREPROCESSOR.max_brightness:.1f}). "
                    f"Please retake the photo in balanced lighting."
                )
            elif prep_status == "failed_no_leaf":
                err = "No crop leaf could be detected in the image. Please center the leaf in the frame with good contrast."
            else:
                err = "Image quality check failed; please upload a clearer leaf image."
            raise ValueError(err)
        stage_finish("preprocessing", t0, "Image preprocessed and quality validated.")

        # 2. Crop Identification
        t0 = stage_start("crop_identification", "Identifying crop species...")
        context = predict_crop(context, _CONFIG)
        crop_label = context.get("crop", {}).get("label") or "Unknown"
        crop_conf = context.get("crop", {}).get("confidence") or 0.0
        stage_finish("crop_identification", t0, f"Detected {crop_label} ({crop_conf * 100:.1f}%)")

        # 3. Decision Routing
        t0 = stage_start("decision_routing", "Selecting crop-specific disease model...")
        context = route_to_disease_model(context, _CONFIG)
        disease_model_name = context.get("disease", {}).get("model_used") or "default"
        stage_finish("decision_routing", t0, f"Routed to model: {disease_model_name}")

        # 4. Disease Classification
        t0 = stage_start("disease_classification", "Classifying crop disease...")
        context = predict_disease(context, _CONFIG)
        disease_label = context.get("disease", {}).get("label") or "Unknown"
        disease_conf = context.get("disease", {}).get("confidence") or 0.0
        stage_finish("disease_classification", t0, f"Classified as {disease_label} ({disease_conf * 100:.1f}%)")

        # 5. Severity Calculation
        t0 = stage_start("severity", "Calculating leaf damage percentage and severity bucket...")
        context = estimate_severity(context)
        severity_pct = context.get("severity", {}).get("percent") or 0.0
        severity_bucket = context.get("severity", {}).get("bucket") or "Unknown"
        stage_finish("severity", t0, f"Severity: {severity_bucket} ({severity_pct}%)", extra_events=["severity_calculation"])

        # 6. Pest Detection
        t0 = stage_start("pest_detection", "Scanning for known agricultural pests...")
        context = predict_pest(context, _CONFIG)
        pests = context.get("pests", [])
        pest_summary = ", ".join([p.get("label", "Pest") for p in pests]) if pests else "No pests detected"
        stage_finish("pest_detection", t0, pest_summary)

        # 7. Weather
        t0 = stage_start("weather", "Fetching current weather conditions...")
        context = fetch_weather(context, _CONFIG)
        weather_status = context.get("weather", {}).get("status", "unknown")
        stage_finish("weather", t0, f"Weather status: {weather_status}")

        # 8. Recommendation
        t0 = stage_start("recommendation", "Synthesizing agronomic advisory...")
        context = generate_recommendation(context, _CONFIG)
        stage_finish("recommendation", t0, "Advisory generated.", extra_events=["llm_advisory"])

        # 9. Persistence & Expert Escalation Check
        t0 = stage_start("persistence", "Saving prediction results...")
        context["image"]["raw_path"] = relative_image_path
        total_duration_ms = round((time.perf_counter() - job_start_time) * 1000)
        context["status"]["pipeline"] = "completed"
        context["stages"]["pipeline"] = {
            "status": "completed",
            "message": "Pipeline completed successfully.",
            "duration_ms": total_duration_ms,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

        thresholds = _CONFIG.get("thresholds", {})
        disease_threshold = thresholds.get("disease_confidence", settings.DISEASE_CONFIDENCE_THRESHOLD)
        crop_threshold = thresholds.get("crop_confidence", settings.CROP_CONFIDENCE_THRESHOLD)

        SCHEMA_VERSION = "2.0.0"
        public_result = _public_result(context)
        public_result["user"] = {"id": user_id}
        public_result["prediction_id"] = prediction_id
        public_result["total_duration_ms"] = total_duration_ms
        public_result["schema_version"] = SCHEMA_VERSION
        public_result["provenance"] = {
            "schema_version": SCHEMA_VERSION,
            "config": {
                "version": "1.0.0",
                "thresholds": {
                    "crop_confidence": crop_threshold,
                    "disease_confidence": disease_threshold,
                },
            },
            "models": {
                "crop": {
                    "name": context.get("crop", {}).get("model_name", "EfficientNet-B0"),
                    "version": context.get("crop", {}).get("model_version", "v1.0"),
                    "model_file": context.get("crop", {}).get("model_file", "crop_identifier_v1.pth"),
                },
                "disease": {
                    "name": context.get("disease", {}).get("model_name", "EfficientNet-B2"),
                    "version": context.get("disease", {}).get("model_version", "v1.0"),
                    "model_file": context.get("disease", {}).get("model_used") or "default",
                },
                "severity": {
                    "name": "HSV Contour Heuristic",
                    "version": "v1.0",
                },
                "pest": {
                    "name": context.get("pest_classification", {}).get("model_name", "YOLO Pest Classifier"),
                    "version": context.get("pest_classification", {}).get("version", "v1.0"),
                    "model_file": context.get("pest_classification", {}).get("model_used") or "pest_classifier/weights/best.pt",
                    "available": context.get("pest_classification", {}).get("available", context.get("status", {}).get("pest_detection") == "completed"),
                },
            },
            "weather_provider": {
                "provider": context.get("weather", {}).get("provider", "OpenWeatherMap"),
                "status": context.get("weather", {}).get("status", "unknown"),
                "is_degraded": context.get("weather", {}).get("is_degraded", False),
                "timestamp": context.get("weather", {}).get("timestamp"),
            },
            "recommendation_provider": {
                "provider": context.get("recommendation", {}).get("provider", "HuggingFace / nscale"),
                "model": context.get("recommendation", {}).get("model", "Qwen/Qwen3-4B-Instruct-2507"),
                "prompt_version": context.get("recommendation", {}).get("prompt_version", "v1.0"),
                "is_fallback": context.get("recommendation", {}).get("is_fallback", False),
                "fallback_reason": context.get("recommendation", {}).get("fallback_reason"),
            },
            "pipeline_duration_ms": total_duration_ms,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        prediction.result = public_result
        prediction.raw_path = relative_image_path
        prediction.processed_path = public_result.get("image", {}).get("processed_path")
        prediction.crop = public_result.get("crop", {}).get("label")
        prediction.crop_conf = public_result.get("crop", {}).get("confidence")
        prediction.disease = public_result.get("disease", {}).get("label")
        prediction.disease_conf = public_result.get("disease", {}).get("confidence")
        prediction.model_used = public_result.get("disease", {}).get("model_used")
        prediction.severity_pct = public_result.get("severity", {}).get("percent")

        disease_confidence = prediction.disease_conf or 0.0
        crop_confidence = prediction.crop_conf or 0.0

        if disease_confidence < disease_threshold:
            ensure_expert_review(db, prediction, "Disease confidence is below the configured threshold.")
            public_result["status"]["expert_review"] = "pending"
        elif crop_confidence < crop_threshold:
            ensure_expert_review(db, prediction, "Crop confidence is below the configured threshold.")
            public_result["status"]["expert_review"] = "pending"
        elif prediction.expert_review is not None and prediction.expert_review.status == "pending":
            prediction.status = "pending_expert_review"
            public_result["status"]["expert_review"] = "pending"
        else:
            prediction.status = "ready"
            public_result["status"]["expert_review"] = "not_requested"

        stage_finish("persistence", t0, f"Persisted with status {prediction.status}")
        db.commit()
        push_status("completed", "completed", "Diagnosis pipeline completed successfully.", total_duration_ms)

    except Exception as exc:
        db.rollback()
        fail_duration_ms = round((time.perf_counter() - current_stage_t0) * 1000)
        now_iso = datetime.now(timezone.utc).isoformat()
        err_msg = str(exc)
        logger.error(f"Prediction {prediction_id} failed during stage '{current_stage}': {err_msg}", exc_info=True)

        prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
        if prediction is not None:
            prediction.status = "failed"
            existing_stages = context.get("stages", {}) if "context" in locals() else {}
            existing_status = context.get("status", {}) if "context" in locals() else {}
            existing_status[current_stage] = "failed"
            existing_status["pipeline"] = "failed"
            existing_stages[current_stage] = {
                "status": "failed",
                "message": err_msg,
                "completed_at": now_iso,
                "duration_ms": fail_duration_ms,
            }
            prediction.result = {
                "prediction_id": prediction_id,
                "error": err_msg,
                "failed_stage": current_stage,
                "status": existing_status,
                "stages": existing_stages,
            }
            db.commit()

        push_status("failed", "failed", err_msg, fail_duration_ms)
        raise
    finally:
        redis_client.close()
        db.close()


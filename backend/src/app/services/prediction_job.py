from __future__ import annotations

import json
import logging
from urllib.parse import urlparse

import redis

from app.context import create_context
from app.core.config import settings
from app.core.paths import resolve_storage_path
from app.core.session import _session_factory
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

    def push_status(stage: str, status: str = "completed") -> None:
        try:
            redis_client.publish(
                f"prediction_status:{prediction_id}",
                json.dumps({"stage": stage, "status": status}),
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

        push_status("preprocessing", "processing")
        context = _PREPROCESSOR.process(context)
        if context["status"]["preprocessing"] != "completed":
            raise ValueError("Image quality check failed; please upload a clearer leaf image.")
        push_status("preprocessing")

        push_status("crop_identification", "processing")
        context = predict_crop(context, _CONFIG)
        context["status"]["crop_identification"] = "completed"
        push_status("crop_identification")

        push_status("disease_classification", "processing")
        context = route_to_disease_model(context, _CONFIG)
        context = predict_disease(context, _CONFIG)
        context = estimate_severity(context)
        context["status"]["disease_classification"] = "completed"
        push_status("disease_classification")
        push_status("severity")

        push_status("pest_detection", "processing")
        context = predict_pest(context, _CONFIG)
        context["status"]["pest_detection"] = "completed"
        push_status("pest_detection")

        push_status("weather", "processing")
        context = fetch_weather(context, _CONFIG)
        push_status("weather")

        push_status("recommendation", "processing")
        context = generate_recommendation(context, _CONFIG)
        push_status("recommendation")

        context["image"]["raw_path"] = relative_image_path
        context["status"]["pipeline"] = "completed"
        public_result = _public_result(context)
        public_result["user"] = {"id": user_id}
        public_result["prediction_id"] = prediction_id

        prediction.result = public_result
        prediction.raw_path = relative_image_path
        prediction.processed_path = public_result.get("image", {}).get("processed_path")
        prediction.crop = public_result.get("crop", {}).get("label")
        prediction.crop_conf = public_result.get("crop", {}).get("confidence")
        prediction.disease = public_result.get("disease", {}).get("label")
        prediction.disease_conf = public_result.get("disease", {}).get("confidence")
        prediction.model_used = public_result.get("disease", {}).get("model_used")
        prediction.severity_pct = public_result.get("severity", {}).get("percent")
        prediction.status = "ready"
        if prediction.expert_review is not None:
            prediction.expert_review.status = "not_requested"
        db.commit()
        push_status("completed")
    except Exception as exc:
        db.rollback()
        prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
        if prediction is not None:
            prediction.status = "failed"
            prediction.result = {"prediction_id": prediction_id, "error": str(exc)}
            db.commit()
        push_status("failed", "failed")
        raise
    finally:
        redis_client.close()
        db.close()

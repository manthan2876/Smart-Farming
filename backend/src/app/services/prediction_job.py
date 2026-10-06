from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone

from app import pipeline as _pipeline
from app.context import create_context
from app.core.config import settings
from app.core.events import prediction_hub
from app.core.paths import resolve_storage_path
from app.core.session import _session_factory
from app.crud.expert_review import ensure_expert_review
from app.models import Prediction
from app.pipeline import (
    SCHEMA_VERSION,
    build_provenance,
    fetch_weather,
    generate_recommendation,
)
from app.services.model_client import call_model_service_sync, merge_and_save_cv_result
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


def _as_float(value) -> float | None:
    """Coerce numpy / Decimal scalars to a plain float so DB drivers never choke on them."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def calculate_treatment_progress(
    parent_pred: Any,
    current_disease: str,
    current_sev_pct: float,
    current_bucket: str,
) -> dict[str, Any]:
    parent_res = parent_pred.result if isinstance(getattr(parent_pred, "result", None), dict) else {}
    parent_sev = getattr(parent_pred, "severity_pct", None)
    if parent_sev is None:
        parent_sev = parent_res.get("severity", {}).get("percent")
    parent_sev = float(parent_sev or 0.0)

    parent_disease = getattr(parent_pred, "disease", None)
    if not parent_disease:
        parent_disease = parent_res.get("disease", {}).get("label") or "Unknown"

    parent_bucket = parent_res.get("severity", {}).get("bucket") or "Unknown"

    delta = round(float(current_sev_pct) - float(parent_sev), 1)
    parent_date_str = parent_pred.created_at.strftime("%b %d") if getattr(parent_pred, "created_at", None) else "previous scan"

    if str(current_disease).lower() == "healthy" or float(current_sev_pct) <= 0.0:
        status = "resolved"
        message = (
            f"Foliar infection appears fully resolved compared to {parent_disease} "
            f"({parent_sev:.1f}% on {parent_date_str}). Foliar tissue is healthy."
        )
    elif delta <= -5.0:
        status = "improving"
        message = (
            f"Foliar infection decreased by {abs(delta):.1f}% (from {parent_sev:.1f}% to {current_sev_pct:.1f}%). "
            "Plant is responding positively to treatment."
        )
    elif delta >= 5.0:
        status = "worsening"
        message = (
            f"Foliar infection increased by {delta:.1f}% (from {parent_sev:.1f}% to {current_sev_pct:.1f}%). "
            "Infection is spreading; review treatment dosage or consult specialist."
        )
    else:
        status = "stable"
        message = (
            f"Foliar infection remains stable (change of {delta:+.1f}% from {parent_sev:.1f}% to {current_sev_pct:.1f}%)."
        )

    if parent_disease != "Unknown" and current_disease != "Unknown" and parent_disease.lower() != current_disease.lower() and current_disease.lower() != "healthy":
        message += f" Diagnosed condition shifted from {parent_disease} to {current_disease}."

    return {
        "parent_prediction_id": parent_pred.id,
        "parent_date": parent_pred.created_at.isoformat() if getattr(parent_pred, "created_at", None) else None,
        "parent_disease": parent_disease,
        "parent_severity_pct": parent_sev,
        "parent_severity_bucket": parent_bucket,
        "current_severity_pct": current_sev_pct,
        "current_severity_bucket": current_bucket,
        "severity_delta": delta,
        "status": status,
        "message": message,
    }


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
    job_start_time = time.perf_counter()
    current_stage = "initialization"
    current_stage_t0 = time.perf_counter()
    context: dict | None = None

    # Read at call time (not import time) so app.pipeline.reload_config() takes effect.
    config = _pipeline._CONFIG

    def push_status(
        stage: str,
        status: str = "completed",
        message: str = "",
        duration_ms: int | None = None,
        data: dict | None = None,
    ) -> None:
        payload = {
            "stage": stage,
            "status": status,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if duration_ms is not None:
            payload["duration_ms"] = duration_ms
        if data:
            payload["data"] = data
        try:
            # Broadcast to in-memory real-time WebSocket subscriber hub (< 1ms latency)
            prediction_hub.publish_sync(
                prediction_id,
                _json_safe(payload),
            )
        except Exception:
            logger.warning(
                "Unable to publish status for prediction %s stage '%s'",
                prediction_id,
                stage,
                exc_info=True,
            )

    try:
        prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
        if prediction is None:
            raise ValueError(f"Prediction {prediction_id} was not found")
        if prediction.status not in {"processing", "failed"}:
            return

        raw_path = resolve_storage_path(relative_image_path)
        if not raw_path.exists():
            raise FileNotFoundError(f"Prediction image not found: {relative_image_path}")

        farm_info = {}
        plot_info = {}
        effective_plot_id = plot_id or prediction.plot_id
        if effective_plot_id:
            from app.models import Plot, Farm
            plot_obj = db.get(Plot, effective_plot_id)
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
            farm_obj = db.query(Farm).filter(Farm.user_id == user_id).first()
            if farm_obj:
                farm_info = {
                    "id": farm_obj.id,
                    "name": farm_obj.name,
                    "location": farm_obj.location,
                    "area_acres": farm_obj.area_acres,
                    "crop_history": farm_obj.crop_history or [],
                }

        context = create_context(
            image_path=str(raw_path),
            user_id=user_id,
            location=location,
            lat=lat,
            lon=lon,
            language=language,
            farm=farm_info,
            plot=plot_info,
        )
        # Make sure every intermediate snapshot saved to the DB (and returned by
        # GET /predictions/{id}) reports the pipeline as running, not "missing".
        context.setdefault("status", {})["pipeline"] = "processing"
        context.setdefault("stages", {})
        prediction.status = "processing"
        db.commit()

        def stage_start(stage_name: str, message: str = "") -> float:
            nonlocal current_stage, current_stage_t0
            current_stage = stage_name
            current_stage_t0 = time.perf_counter()
            now_iso = datetime.now(timezone.utc).isoformat()
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

        def stage_finish(
            stage_name: str,
            t0: float,
            message: str = "",
            extra_events: list[str] | None = None,
            data: dict | None = None,
            persist: bool = True,
        ) -> int:
            duration_ms = round((time.perf_counter() - t0) * 1000)
            now_iso = datetime.now(timezone.utc).isoformat()

            # A stage may have set its own terminal status ("skipped", "failed", "degraded"...).
            # Only promote the default "processing" marker, exactly like pipeline.run_pipeline.
            if context["status"].get(stage_name, "processing") == "processing":
                context["status"][stage_name] = "completed"
            final_status = context["status"][stage_name]

            context["stages"].setdefault(stage_name, {})
            context["stages"][stage_name].update({
                "status": final_status,
                "message": message,
                "completed_at": now_iso,
                "duration_ms": duration_ms,
            })

            # Persist intermediate progress so REST polling reflects it too.
            # (Skipped for the final "persistence" stage: the caller writes the complete
            # result itself, and persisting here would overwrite it with a bare snapshot.)
            if persist:
                try:
                    prediction.result = _public_result(context)
                    if data:
                        if data.get("crop"):
                            prediction.crop = data["crop"].get("label")
                            prediction.crop_conf = _as_float(data["crop"].get("confidence"))
                        if data.get("disease"):
                            prediction.disease = data["disease"].get("label")
                            prediction.disease_conf = _as_float(data["disease"].get("confidence"))
                            prediction.model_used = data["disease"].get("model_used")
                        if data.get("severity"):
                            prediction.severity_pct = _as_float(data["severity"].get("percent"))
                    db.commit()
                except Exception:
                    db.rollback()
                    logger.warning(
                        "Failed to persist progress for prediction %s stage '%s'",
                        prediction_id,
                        stage_name,
                        exc_info=True,
                    )

            current_data = {
                "crop": context.get("crop"),
                "disease": context.get("disease"),
                "pests": context.get("pests"),
                "severity": context.get("severity"),
            }
            if data:
                current_data.update(data)

            # Always "completed" on the wire: a stage that degrades gracefully ("skipped", etc.)
            # is still finished from the client's point of view. A real failure raises instead.
            push_status(stage_name, "completed", message, duration_ms, data=current_data)
            if extra_events:
                for extra_stage in extra_events:
                    push_status(extra_stage, "completed", message, duration_ms, data=current_data)
            return duration_ms

        # Read image binary
        image_bytes = raw_path.read_bytes()

        # 1. Preprocessing & Computer Vision Pipeline (via Model Server)
        t0 = stage_start("preprocessing", "Validating image quality and clarity...")
        cv_result = call_model_service_sync(image_bytes, raw_path.name)
        stage_finish("preprocessing", t0, "Image preprocessed and quality validated.")

        # 2. Crop Identification
        t0 = stage_start("crop_identification", "Identifying crop species...")
        context.setdefault("crop", {}).update(cv_result.get("crop", {}))
        crop_label = context.get("crop", {}).get("label") or "Unknown"
        crop_conf = context.get("crop", {}).get("confidence") or 0.0
        stage_finish(
            "crop_identification",
            t0,
            f"Detected {crop_label} ({crop_conf * 100:.1f}%)",
            data={"crop": context.get("crop")},
        )

        # 3. Decision Routing
        t0 = stage_start("decision_routing", "Selecting crop-specific disease model...")
        routing_status = cv_result.get("status", {}).get("decision_routing", "completed")
        disease_model_name = cv_result.get("disease", {}).get("model_used") or "default"
        if routing_status == "unsupported_crop":
            routing_msg = f"Crop '{crop_label}' is unsupported for automated disease diagnosis. Specialist inspection advised."
        else:
            routing_msg = f"Routed to model: {disease_model_name}"
        stage_finish(
            "decision_routing",
            t0,
            routing_msg,
            data={"disease": cv_result.get("disease"), "crop": cv_result.get("crop")},
        )

        # 4. Disease Classification
        t0 = stage_start("disease_classification", "Classifying crop disease...")
        context.setdefault("disease", {}).update(cv_result.get("disease", {}))
        disease_label = context.get("disease", {}).get("label") or "Unknown"
        disease_conf = context.get("disease", {}).get("confidence") or 0.0
        stage_finish(
            "disease_classification",
            t0,
            f"Classified as {disease_label} ({disease_conf * 100:.1f}%)",
            data={"disease": context.get("disease")},
        )

        # 5. Severity Calculation
        t0 = stage_start("severity", "Calculating leaf damage percentage and severity bucket...")
        context.setdefault("severity", {}).update(cv_result.get("severity", {}))
        severity_pct = context.get("severity", {}).get("percent") or 0.0
        severity_bucket = context.get("severity", {}).get("bucket") or "Unknown"
        stage_finish(
            "severity",
            t0,
            f"Severity: {severity_bucket} ({severity_pct}%)",
            extra_events=["severity_calculation"],
            data={"severity": context.get("severity")},
        )

        # 6. Pest Detection
        t0 = stage_start("pest_detection", "Scanning for known agricultural pests...")
        context["pests"] = cv_result.get("pests", [])
        context.setdefault("pest_classification", {}).update(cv_result.get("pest_classification", {}))
        pests = context.get("pests", [])
        pest_status = context.get("pest_classification", {}).get("status")
        pest_det_status = cv_result.get("status", {}).get("pest_detection", "completed")

        if pest_status == "unavailable" or pest_det_status in ("unavailable", "skipped"):
            pest_summary = "Pest detection model unavailable"
        elif not pests or pest_status == "no_pests_detected":
            pest_summary = "No pests detected"
        else:
            pest_summary = ", ".join([p.get("label", "Pest") for p in pests])

        stage_finish(
            "pest_detection",
            t0,
            pest_summary,
            data={"pests": pests, "pest_classification": context.get("pest_classification")},
        )

        # Merge remaining context fields from model service & persist processed Grad-CAM image
        merge_and_save_cv_result(context, cv_result, raw_path.name)

        # 7. Weather
        t0 = stage_start("weather", "Fetching current weather conditions...")
        context = fetch_weather(context, config)
        weather_status = context.get("weather", {}).get("status", "unknown")
        stage_finish(
            "weather",
            t0,
            f"Weather status: {weather_status}",
            data={"weather": context.get("weather")},
        )

        # 8. Recommendation
        t0 = stage_start("recommendation", "Synthesizing agronomic advisory...")
        context = generate_recommendation(context, config)
        stage_finish(
            "recommendation",
            t0,
            "Advisory generated.",
            extra_events=["llm_advisory"],
            data={"recommendation": context.get("recommendation")},
        )

        # 9. Persistence & Expert Escalation Check
        t0 = stage_start("persistence", "Saving prediction results...")
        context["image"]["raw_path"] = relative_image_path
        total_duration_ms = round((time.perf_counter() - job_start_time) * 1000)

        # Close out the persistence stage and the pipeline in the context *before* the final
        # snapshot is taken, and without a DB write (persist=False): the complete result is
        # assembled and saved once, below.
        stage_finish("persistence", t0, "Prediction results saved.", persist=False)
        context["status"]["pipeline"] = "completed"
        context["stages"]["pipeline"] = {
            "status": "completed",
            "message": "Pipeline completed successfully.",
            "duration_ms": total_duration_ms,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

        thresholds = config.get("thresholds", {})
        disease_threshold = thresholds.get("disease_confidence", settings.DISEASE_CONFIDENCE_THRESHOLD)
        crop_threshold = thresholds.get("crop_confidence", settings.CROP_CONFIDENCE_THRESHOLD)

        # Write-time translation architecture:
        # Load any existing translations from entity_translations table (instant lookup)
        from app.models.translation import EntityTranslation
        from app.services.translation.service import normalize_language_code
        target_code = normalize_language_code(language)
        translations: dict[str, Any] = {}

        try:
            cached_trans = db.query(EntityTranslation).filter_by(
                entity_type="prediction",
                entity_id=str(prediction_id),
                status="done",
            ).all()
            for ct in cached_trans:
                if ct.language not in translations:
                    translations[ct.language] = dict(context.get("recommendation", {}))
                    translations[ct.language]["language"] = ct.language
                translations[ct.language][ct.field_name] = ct.translated_text
        except Exception:
            pass

        public_result = _public_result(context)
        # Location/lat/lon/language are stored so a later rescan can reuse them.
        public_result["user"] = {
            **(public_result.get("user") or {}),
            "id": user_id,
            "location": location,
            "lat": lat,
            "lon": lon,
            "language": language,
        }
        public_result["prediction_id"] = prediction_id
        public_result["total_duration_ms"] = total_duration_ms
        public_result["schema_version"] = SCHEMA_VERSION
        public_result["provenance"] = build_provenance(context, total_duration_ms)
        public_result["translations"] = translations

        prediction.raw_path = relative_image_path
        prediction.processed_path = public_result.get("image", {}).get("processed_path")
        prediction.crop = public_result.get("crop", {}).get("label")
        prediction.crop_conf = _as_float(public_result.get("crop", {}).get("confidence"))
        prediction.disease = public_result.get("disease", {}).get("label")
        prediction.disease_conf = _as_float(public_result.get("disease", {}).get("confidence"))
        prediction.model_used = public_result.get("disease", {}).get("model_used")
        prediction.severity_pct = _as_float(public_result.get("severity", {}).get("percent"))

        disease_confidence = prediction.disease_conf or 0.0
        crop_confidence = prediction.crop_conf or 0.0

        is_near_tie = public_result.get("disease", {}).get("is_near_tie", False)
        could_also_be_info = public_result.get("disease", {}).get("could_also_be")

        is_unsupported_crop = (
            public_result.get("crop", {}).get("status") == "unsupported_crop"
            or public_result.get("status", {}).get("decision_routing") == "unsupported_crop"
            or crop_confidence < crop_threshold
        )

        review_reason: str | None = None
        if is_unsupported_crop:
            crop_name = public_result.get("crop", {}).get("label") or "Unknown Crop"
            review_reason = (
                f"Crop '{crop_name}' is unsupported or identified with low confidence ({crop_confidence * 100:.1f}%). "
                "Automated disease models support Cotton, Groundnut, Pepper Bell, Potato, and Tomato."
            )
            public_result["status"]["mask_advisory"] = True
        elif is_near_tie:
            alt_lbl = could_also_be_info.get("label", "alternative candidate") if isinstance(could_also_be_info, dict) else "alternative candidate"
            review_reason = f"Near-tie diagnosis with alternative candidate '{alt_lbl}'. Flagged for expert verification."
        elif disease_confidence < disease_threshold:
            review_reason = "Disease confidence is below the configured threshold."
        already_pending = (
            prediction.expert_review is not None and prediction.expert_review.status == "pending"
        )

        # Compute treatment progress if this is a follow-up/rescan
        effective_parent_id = parent_id or prediction.parent_id
        if effective_parent_id:
            parent_pred = db.query(Prediction).filter(Prediction.id == effective_parent_id).first()
            if parent_pred:
                cur_disease = public_result.get("disease", {}).get("label") or "Unknown"
                cur_sev = _as_float(public_result.get("severity", {}).get("percent")) or 0.0
                cur_bucket = public_result.get("severity", {}).get("bucket") or "Unknown"
                public_result["treatment_progress"] = calculate_treatment_progress(
                    parent_pred, cur_disease, cur_sev, cur_bucket
                )

        if plot_info:
            public_result["plot"] = plot_info
        if farm_info:
            public_result["farm"] = farm_info

        prediction.result = public_result

        if review_reason:
            ensure_expert_review(db, prediction, review_reason)
            if prediction.status == "processing":
                prediction.status = "pending_expert_review"
        elif already_pending:
            prediction.status = "pending_expert_review"
        else:
            prediction.status = "ready"

        db.commit()

        # Enqueue background translation to Redis (does not block user or pipeline)
        canonical_rec = context.get("recommendation", {})
        if canonical_rec and isinstance(canonical_rec, dict):
            rec_fields = {}
            for k in [
                "immediate_action", "treatment", "prevention", "monitoring",
                "safety_disclaimer", "action", "fertilizer", "pesticide",
                "irrigation", "prevention_tips"
            ]:
                v = canonical_rec.get(k)
                if v and isinstance(v, str) and v.strip():
                    rec_fields[k] = v.strip()
            if rec_fields:
                try:
                    from app.core.arq import enqueue_translation_sync
                    enqueue_translation_sync("prediction", prediction_id, rec_fields)
                except Exception as enq_err:
                    logger.warning("Could not enqueue prediction translation to Redis: %s", enq_err)

        push_status(
            "completed",
            "completed",
            "Diagnosis pipeline completed successfully.",
            total_duration_ms,
            # Full final snapshot: lets the client recover even if earlier live events were lost.
            data={
                "crop": public_result.get("crop"),
                "disease": public_result.get("disease"),
                "pests": public_result.get("pests"),
                "severity": public_result.get("severity"),
            },
        )

    except Exception as exc:
        db.rollback()
        fail_duration_ms = round((time.perf_counter() - current_stage_t0) * 1000)
        now_iso = datetime.now(timezone.utc).isoformat()
        err_msg = str(exc)
        logger.error(f"Prediction {prediction_id} failed during stage '{current_stage}': {err_msg}", exc_info=True)

        try:
            prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
            if prediction is not None:
                prediction.status = "failed"
                existing_stages = context.get("stages", {}) if context else {}
                existing_status = context.get("status", {}) if context else {}
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
        except Exception:
            db.rollback()
            logger.error("Could not record failure for prediction %s", prediction_id, exc_info=True)

        push_status("failed", "failed", err_msg, fail_duration_ms)
        raise
    finally:
        db.close()
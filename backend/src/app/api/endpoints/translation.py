from __future__ import annotations

import logging
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.api.deps import get_current_user
from app.core import get_session
from app.models import Prediction
from app.services.translation.service import (
    translate_recommendation,
    normalize_language_code,
)

logger = logging.getLogger("smart-farming.api.translation")

router = APIRouter(prefix="/predictions", tags=["translation"])


@router.post("/{prediction_id}/translate")
async def translate_prediction_recommendation(
    prediction_id: int,
    target_language: str = Query(..., description="Target language: 'Hindi', 'Gujarati', 'English', or code 'hi', 'gu', 'en'"),
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """
    Translate the recommendation and expert guidance for a prediction on-demand.

    - If requested in English, returns the canonical English recommendation.
    - If already translated and cached in prediction.result["translations"][lang_code], returns from cache (0 ms).
    - Otherwise, translates using Google Cloud Translation API v2, caches in the database, and returns.
    """
    pred = session.get(Prediction, prediction_id)
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")

    target_code = normalize_language_code(target_language)
    res = dict(pred.result or {})
    canonical_rec = res.get("recommendation", {})

    # If target is English, return canonical recommendation
    if target_code == "en":
        return {
            "prediction_id": prediction_id,
            "language": "en",
            "cached": True,
            "recommendation": canonical_rec,
        }

    translations = res.setdefault("translations", {})
    if target_code in translations and translations[target_code]:
        return {
            "prediction_id": prediction_id,
            "language": target_code,
            "cached": True,
            "recommendation": translations[target_code],
            "translations": translations,
        }

    # Check EntityTranslation table first (0 ms external API latency)
    from app.models.translation import EntityTranslation
    db_translations = session.query(EntityTranslation).filter_by(
        entity_type="prediction",
        entity_id=str(prediction_id),
        language=target_code,
        status="done",
    ).all()
    if db_translations:
        db_rec = dict(canonical_rec)
        db_rec["language"] = target_code
        for tr in db_translations:
            db_rec[tr.field_name] = tr.translated_text
        translations[target_code] = db_rec
        res["translations"] = translations
        pred.result = res
        flag_modified(pred, "result")
        session.commit()
        return {
            "prediction_id": prediction_id,
            "language": target_code,
            "cached": True,
            "recommendation": db_rec,
            "translations": translations,
        }

    # Translate on-demand
    if not canonical_rec:
        raise HTTPException(status_code=400, detail="Prediction has no recommendation to translate")

    try:
        translated_rec = await translate_recommendation(canonical_rec, target_code)
        translations = dict(res.get("translations") or {})
        translations[target_code] = translated_rec
        res["translations"] = translations
        pred.result = res
        flag_modified(pred, "result")

        # Persist to EntityTranslation table
        from app.services.translation.manager import compute_hash
        for f_name, f_val in translated_rec.items():
            if f_name in ["immediate_action", "treatment", "prevention", "monitoring", "safety_disclaimer"] and isinstance(f_val, str):
                orig_val = canonical_rec.get(f_name, "")
                existing = session.query(EntityTranslation).filter_by(
                    entity_type="prediction",
                    entity_id=str(prediction_id),
                    field_name=f_name,
                    language=target_code,
                ).first()
                if existing:
                    existing.translated_text = f_val
                    existing.source_hash = compute_hash(orig_val)
                    existing.status = "done"
                else:
                    session.add(EntityTranslation(
                        entity_type="prediction",
                        entity_id=str(prediction_id),
                        field_name=f_name,
                        language=target_code,
                        translated_text=f_val,
                        source_hash=compute_hash(orig_val),
                        is_transliteration=False,
                        status="done",
                        retries=0,
                    ))

        session.add(pred)
        session.commit()
        session.refresh(pred)

    except Exception as exc:
        logger.warning(
            "On-demand translation failed for prediction #%d: %s; falling back to canonical English",
            prediction_id, exc
        )
        return {
            "prediction_id": prediction_id,
            "language": "en",
            "cached": False,
            "recommendation": canonical_rec,
            "translation_status": "degraded",
            "warning": "Translation services currently unavailable. Displaying original English.",
        }



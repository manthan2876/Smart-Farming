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
    - Otherwise, translates using IndicTrans2 on Colab/GPU server, caches in the database, and returns.
    """
    pred = session.get(Prediction, prediction_id)
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")

    target_code = normalize_language_code(target_language)
    res = dict(pred.result or {})
    canonical_rec = res.get("recommendation", {})

    # Locate any expert review attached to this prediction or its latest follow-up
    from app.models.translation import EntityTranslation
    er = pred.expert_review
    if not er and getattr(pred, "follow_ups", None) and pred.follow_ups:
        er = pred.follow_ups[-1].expert_review

    async def _resolve_expert_guidance(target_lang_code: str) -> str | None:
        if not er or getattr(er, "status", None) != "verified" or not er.farmer_guidance or not er.farmer_guidance.strip():
            return None
        source_guidance = er.farmer_guidance.strip()
        existing_guidance_trans = session.query(EntityTranslation).filter_by(
            entity_type="expert_review",
            entity_id=str(er.id),
            field_name="farmer_guidance",
            language=target_lang_code,
            status="done",
        ).first()
        if existing_guidance_trans and existing_guidance_trans.translated_text:
            return existing_guidance_trans.translated_text
        if target_lang_code == "en" and not any(ord(c) >= 0x0900 for c in source_guidance):
            return source_guidance
        if target_lang_code == "gu" and any(0x0A80 <= ord(c) <= 0x0AFF for c in source_guidance):
            return source_guidance
        if target_lang_code == "hi" and any(0x0900 <= ord(c) <= 0x097F for c in source_guidance):
            return source_guidance

        try:
            from app.services.translation.service import translate_text
            from app.services.translation.manager import compute_hash
            translated_guidance = await translate_text(source_guidance, target_lang_code)
            if translated_guidance:
                if existing_guidance_trans:
                    existing_guidance_trans.translated_text = translated_guidance
                    existing_guidance_trans.status = "done"
                else:
                    session.add(EntityTranslation(
                        entity_type="expert_review",
                        entity_id=str(er.id),
                        field_name="farmer_guidance",
                        language=target_lang_code,
                        translated_text=translated_guidance,
                        source_hash=compute_hash(source_guidance),
                        is_transliteration=False,
                        status="done",
                        retries=0,
                    ))
                session.commit()
                return translated_guidance
        except Exception as e:
            logger.warning("Failed to translate expert guidance for prediction %s: %s", prediction_id, e)
        return source_guidance

    expert_guidance_val = await _resolve_expert_guidance(target_code)

    # If target is English, return canonical recommendation and English guidance
    if target_code == "en":
        return {
            "prediction_id": prediction_id,
            "language": "en",
            "cached": True,
            "recommendation": canonical_rec,
            "expert_guidance": expert_guidance_val,
        }

    def _rec_has_indic(rec: dict[str, Any]) -> bool:
        for k, v in rec.items():
            if k != "language" and isinstance(v, str) and any(ord(c) >= 0x0900 for c in v):
                return True
        return False

    translations = res.setdefault("translations", {})
    if target_code in translations and translations[target_code]:
        if target_code not in ("hi", "gu") or _rec_has_indic(translations[target_code]):
            if expert_guidance_val:
                translations[target_code]["farmer_guidance"] = expert_guidance_val
            return {
                "prediction_id": prediction_id,
                "language": target_code,
                "cached": True,
                "recommendation": translations[target_code],
                "expert_guidance": expert_guidance_val,
                "translations": translations,
            }
        logger.info("Discarding stale non-Indic cached translation for %s (prediction %s)", target_code, prediction_id)

    # Check EntityTranslation table first (0 ms external API latency)
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
        if target_code not in ("hi", "gu") or _rec_has_indic(db_rec):
            if expert_guidance_val:
                db_rec["farmer_guidance"] = expert_guidance_val
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
                "expert_guidance": expert_guidance_val,
                "translations": translations,
            }

    # Translate on-demand
    if not canonical_rec and not expert_guidance_val:
        raise HTTPException(status_code=400, detail="Prediction has no recommendation or expert guidance to translate")

    try:
        translated_rec = await translate_recommendation(canonical_rec, target_code) if canonical_rec else {}
        if expert_guidance_val:
            translated_rec["farmer_guidance"] = expert_guidance_val

        if not canonical_rec or (target_code not in ("hi", "gu") or _rec_has_indic(translated_rec)):
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

        return {
            "prediction_id": prediction_id,
            "language": target_code,
            "cached": False,
            "recommendation": translated_rec,
            "expert_guidance": expert_guidance_val,
            "translations": translations,
        }

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
            "expert_guidance": expert_guidance_val,
            "translation_status": "degraded",
            "warning": "Translation services currently unavailable. Displaying original English.",
        }



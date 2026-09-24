from __future__ import annotations

import hashlib
import logging
from typing import Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.translation import EntityTranslation
from app.services.translation.service import translate_batch_google_sync
from app.services.translation.transliteration import transliterate_name

logger = logging.getLogger("smart-farming.translation.manager")

SUPPORTED_LANGUAGES: list[str] = ["gu", "hi"]


def compute_hash(text: str) -> str:
    """Compute SHA256 hash of normalized source text for change detection."""
    return hashlib.sha256((text or "").strip().encode("utf-8")).hexdigest()


def process_entity_translation_sync(
    session: Session,
    entity_type: str,
    entity_id: str,
    fields: dict[str, str],
    name_fields: list[str] | None = None,
) -> dict[str, int]:
    """Execute write-time translation/transliteration for an entity's fields into Hindi and Gujarati.

    Deduplication:
        Checks SHA256 of source text. If an entry already exists with identical source_hash
        and status 'done', the external API call is skipped.

    Error Handling:
        Failed translation attempts update the translation row with status='failed'
        and record the error message, re-raising so ARQ worker retries can be applied.
    """
    name_fields_set = set(name_fields or [])
    stats = {"translated": 0, "skipped": 0, "failed": 0}

    for field_name, source_text in fields.items():
        if not source_text or not isinstance(source_text, str) or not source_text.strip():
            continue

        clean_text = source_text.strip()
        src_hash = compute_hash(clean_text)
        is_name = field_name in name_fields_set

        for lang in SUPPORTED_LANGUAGES:
            existing = session.query(EntityTranslation).filter_by(
                entity_type=entity_type,
                entity_id=str(entity_id),
                field_name=field_name,
                language=lang,
            ).first()

            # Skip translation if identical source has already been translated
            if existing and existing.source_hash == src_hash and existing.status == "done":
                stats["skipped"] += 1
                continue

            try:
                if is_name:
                    translated_val = transliterate_name(clean_text, lang)
                else:
                    batch_res = translate_batch_google_sync([clean_text], lang)
                    translated_val = batch_res[0] if batch_res else clean_text

                if existing:
                    existing.translated_text = translated_val
                    existing.source_hash = src_hash
                    existing.is_transliteration = is_name
                    existing.status = "done"
                    existing.last_error = None
                    existing.updated_at = datetime.now(timezone.utc)
                else:
                    new_rec = EntityTranslation(
                        entity_type=entity_type,
                        entity_id=str(entity_id),
                        field_name=field_name,
                        language=lang,
                        translated_text=translated_val,
                        source_hash=src_hash,
                        is_transliteration=is_name,
                        status="done",
                        retries=0,
                        last_error=None,
                    )
                    session.add(new_rec)

                session.commit()
                stats["translated"] += 1
                logger.info(
                    "Translated %s #%s field '%s' -> %s (%d chars)",
                    entity_type, entity_id, field_name, lang, len(translated_val)
                )
            except Exception as err:
                session.rollback()
                logger.error(
                    "Failed translating %s #%s field '%s' into %s: %s",
                    entity_type, entity_id, field_name, lang, err
                )
                stats["failed"] += 1

                # Record error in translation table for auditing and status inspection
                try:
                    if existing:
                        existing.status = "failed"
                        existing.retries += 1
                        existing.last_error = str(err)
                        session.commit()
                    else:
                        failed_rec = EntityTranslation(
                            entity_type=entity_type,
                            entity_id=str(entity_id),
                            field_name=field_name,
                            language=lang,
                            translated_text="",
                            source_hash=src_hash,
                            is_transliteration=is_name,
                            status="failed",
                            retries=1,
                            last_error=str(err),
                        )
                        session.add(failed_rec)
                        session.commit()
                except Exception:
                    session.rollback()

                raise

    # If entity is a prediction, sync available translations to prediction.result for direct client access
    if entity_type == "prediction":
        try:
            from app.models import Prediction
            from sqlalchemy.orm.attributes import flag_modified
            pred = session.get(Prediction, int(entity_id))
            if pred and pred.result:
                res = dict(pred.result)
                translations = dict(res.get("translations") or {})
                for lang in SUPPORTED_LANGUAGES:
                    lang_recs = session.query(EntityTranslation).filter_by(
                        entity_type="prediction",
                        entity_id=str(entity_id),
                        language=lang,
                        status="done",
                    ).all()
                    if lang_recs:
                        t_rec = dict(res.get("recommendation") or {})
                        t_rec["language"] = lang
                        for r in lang_recs:
                            t_rec[r.field_name] = r.translated_text
                        translations[lang] = t_rec
                res["translations"] = translations
                pred.result = res
                flag_modified(pred, "result")
                session.commit()
        except Exception as sync_err:
            logger.warning("Failed updating prediction.result translations: %s", sync_err)

    return stats

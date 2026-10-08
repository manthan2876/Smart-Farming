from __future__ import annotations

import logging
from typing import Any, Callable, TypeVar
from sqlalchemy.orm import Session
from app.models.translation import EntityTranslation

logger = logging.getLogger("smart-farming.translation")

T = TypeVar("T")


def _is_valid_indic(trans: str | None, orig: str | None, lang_code: str) -> bool:
    """Validate that a translated text for Hindi or Gujarati actually contains Indic characters."""
    if not trans or not trans.strip():
        return False
    if not orig or not orig.strip():
        return True
    if lang_code in ("hi", "gu"):
        clean_orig = orig.strip()
        # If source has alphabetic characters, the translation must contain Indic characters (>= 0x0900)
        if any(c.isalpha() for c in clean_orig):
            if not any(ord(c) >= 0x0900 for c in trans):
                return False
    return True


def overlay_entity_translations(
    session: Session,
    entities: list[T],
    entity_type: str,
    id_getter: Callable[[T], str | int],
    fields: list[str],
    language: str | None,
    name_fields: list[str] | None = None,
) -> list[T]:
    """Overlay translations on a list of entities in-memory with automatic self-healing fallback."""
    if not language or language.lower().startswith("en") or not entities:
        return entities

    lang_code = "gu" if language.lower().startswith("gu") else "hi" if language.lower().startswith("hi") else None
    if not lang_code:
        return entities

    name_fields_set = set(name_fields or [])

    entity_ids = []
    for entity in entities:
        try:
            entity_ids.append(str(id_getter(entity)))
        except Exception:
            continue

    if not entity_ids:
        return entities

    # Single batched SQL query for all entities in the page/result
    translations = session.query(EntityTranslation).filter(
        EntityTranslation.entity_type == entity_type,
        EntityTranslation.entity_id.in_(entity_ids),
        EntityTranslation.language == lang_code,
        EntityTranslation.status == "done",
    ).all()

    # Fast lookup table: { (entity_id, field_name): EntityTranslation }
    trans_records: dict[tuple[str, str], EntityTranslation] = {
        (t.entity_id, t.field_name): t for t in translations
    }
    lookup: dict[tuple[str, str], str] = {
        (t.entity_id, t.field_name): t.translated_text for t in translations if t.translated_text
    }

    # Identify and self-heal missing or invalid (untranslated ASCII) translations on the fly
    records_to_save = []
    for entity in entities:
        try:
            eid = str(id_getter(entity))
        except Exception:
            continue

        for field in fields:
            key = (eid, field)
            source_text = None
            if isinstance(entity, dict):
                source_text = entity.get(field)
            elif hasattr(entity, field):
                source_text = getattr(entity, field, None)

            if not source_text or not isinstance(source_text, str) or not source_text.strip():
                continue

            clean_source = source_text.strip()
            existing_val = lookup.get(key)

            # Heal if translation is missing OR if Indic translation is invalid (still English ASCII)
            if not existing_val or not _is_valid_indic(existing_val, clean_source, lang_code):
                is_name = field in name_fields_set
                try:
                    if is_name:
                        from app.services.translation.transliteration import transliterate_name
                        trans_val = transliterate_name(clean_source, lang_code)
                    else:
                        from app.services.translation.service import translate_batch_sync
                        batch_res = translate_batch_sync([clean_source], lang_code)
                        trans_val = batch_res[0] if batch_res else clean_source

                    if trans_val and trans_val != clean_source:
                        lookup[key] = trans_val
                        from app.services.translation.manager import compute_hash
                        if key in trans_records:
                            rec = trans_records[key]
                            rec.translated_text = trans_val
                            rec.source_hash = compute_hash(clean_source)
                            rec.is_transliteration = is_name
                            rec.status = "done"
                            records_to_save.append(rec)
                        else:
                            new_rec = EntityTranslation(
                                entity_type=entity_type,
                                entity_id=eid,
                                field_name=field,
                                language=lang_code,
                                translated_text=trans_val,
                                source_hash=compute_hash(clean_source),
                                is_transliteration=is_name,
                                status="done",
                                retries=0,
                            )
                            records_to_save.append(new_rec)
                except Exception as err:
                    logger.debug("On-the-fly translation error for %s #%s field '%s': %s", entity_type, eid, field, err)

    if records_to_save:
        try:
            for rec in records_to_save:
                session.add(rec)
            session.commit()
            logger.info("Auto-healed and persisted %d missing/invalid translations for %s", len(records_to_save), entity_type)
        except Exception as commit_err:
            session.rollback()
            logger.debug("Failed saving auto-healed translations: %s", commit_err)

    for entity in entities:
        try:
            eid = str(id_getter(entity))
        except Exception:
            continue

        for field in fields:
            key = (eid, field)
            if key in lookup:
                val = lookup[key]
                if isinstance(entity, dict):
                    entity[field] = val
                elif hasattr(entity, field):
                    setattr(entity, field, val)

    return entities


def overlay_dict_translations(
    session: Session,
    data: dict[str, Any],
    entity_type: str,
    entity_id: str | int,
    fields: list[str],
    language: str | None,
    name_fields: list[str] | None = None,
) -> dict[str, Any]:
    """Helper to overlay translations on a single dictionary response object with on-the-fly auto-healing."""
    if not language or language.lower().startswith("en") or not data:
        return data

    lang_code = "gu" if language.lower().startswith("gu") else "hi" if language.lower().startswith("hi") else None
    if not lang_code:
        return data

    name_fields_set = set(name_fields or [])

    translations = session.query(EntityTranslation).filter(
        EntityTranslation.entity_type == entity_type,
        EntityTranslation.entity_id == str(entity_id),
        EntityTranslation.language == lang_code,
        EntityTranslation.status == "done",
    ).all()

    trans_map: dict[str, EntityTranslation] = {t.field_name: t for t in translations}
    for t in translations:
        if t.field_name in fields and t.translated_text:
            data[t.field_name] = t.translated_text

    # Self-heal any missing OR invalid (untranslated ASCII) fields
    records_to_save = []
    for field in fields:
        clean_source = str(data.get(field) or "").strip()
        if not clean_source:
            continue

        current_val = data.get(field)
        is_missing = field not in trans_map
        is_invalid = not _is_valid_indic(current_val, clean_source, lang_code)

        if is_missing or is_invalid:
            is_name = field in name_fields_set
            try:
                if is_name:
                    from app.services.translation.transliteration import transliterate_name
                    trans_val = transliterate_name(clean_source, lang_code)
                else:
                    from app.services.translation.service import translate_batch_sync
                    batch_res = translate_batch_sync([clean_source], lang_code)
                    trans_val = batch_res[0] if batch_res else clean_source

                if trans_val and trans_val != clean_source:
                    data[field] = trans_val
                    from app.services.translation.manager import compute_hash
                    if field in trans_map:
                        rec = trans_map[field]
                        rec.translated_text = trans_val
                        rec.source_hash = compute_hash(clean_source)
                        rec.is_transliteration = is_name
                        rec.status = "done"
                        records_to_save.append(rec)
                    else:
                        new_rec = EntityTranslation(
                            entity_type=entity_type,
                            entity_id=str(entity_id),
                            field_name=field,
                            language=lang_code,
                            translated_text=trans_val,
                            source_hash=compute_hash(clean_source),
                            is_transliteration=is_name,
                            status="done",
                            retries=0,
                        )
                        records_to_save.append(new_rec)
            except Exception as err:
                logger.debug("On-the-fly dict translation error for %s #%s field '%s': %s", entity_type, entity_id, field, err)

    if records_to_save:
        try:
            for rec in records_to_save:
                session.add(rec)
            session.commit()
            logger.info("Auto-healed and persisted %d missing/invalid dict translations for %s", len(records_to_save), entity_type)
        except Exception:
            session.rollback()

    return data


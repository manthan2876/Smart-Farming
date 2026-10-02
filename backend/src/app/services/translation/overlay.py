import logging
from typing import Any, Callable
from sqlalchemy.orm import Session
from app.models.translation import EntityTranslation

logger = logging.getLogger("smart-farming.translation.overlay")


def overlay_entity_translations(
    session: Session,
    entities: list[Any],
    entity_type: str,
    id_getter: Callable[[Any], Any],
    fields: list[str],
    language: str | None,
    name_fields: list[str] | None = None,
) -> list[Any]:
    """Overlay pre-translated fields onto model instances or dicts in a single batch query.

    If language is 'en', None, or unsupported, returns entities unmodified.
    If a translation for a given field is missing from the DB, it translates/transliterates
    on the fly, persists to entity_translations, and returns the translated text.
    """
    if not language or language.lower().startswith("en") or not entities:
        return entities

    lang_code = "gu" if language.lower().startswith("gu") else "hi" if language.lower().startswith("hi") else None
    if not lang_code:
        return entities

    name_fields_set = set(name_fields or [])

    # Extract all entity IDs
    entity_ids: list[str] = []
    for e in entities:
        try:
            eid = str(id_getter(e))
            if eid:
                entity_ids.append(eid)
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

    # Fast lookup table: { (entity_id, field_name): translated_text }
    lookup: dict[tuple[str, str], str] = {
        (t.entity_id, t.field_name): t.translated_text for t in translations if t.translated_text
    }

    # Identify and self-heal missing translations on the fly
    new_translations_to_add = []
    for entity in entities:
        try:
            eid = str(id_getter(entity))
        except Exception:
            continue

        for field in fields:
            key = (eid, field)
            if key not in lookup or not lookup[key]:
                source_text = None
                if isinstance(entity, dict):
                    source_text = entity.get(field)
                elif hasattr(entity, field):
                    source_text = getattr(entity, field, None)

                if source_text and isinstance(source_text, str) and source_text.strip():
                    clean_source = source_text.strip()
                    is_name = field in name_fields_set
                    try:
                        if is_name:
                            from app.services.translation.transliteration import transliterate_name
                            trans_val = transliterate_name(clean_source, lang_code)
                        else:
                            from app.services.translation.service import translate_batch_google_sync
                            batch_res = translate_batch_google_sync([clean_source], lang_code)
                            trans_val = batch_res[0] if batch_res else clean_source

                        if trans_val and trans_val != clean_source:
                            lookup[key] = trans_val
                            from app.services.translation.manager import compute_hash
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
                            new_translations_to_add.append(new_rec)
                    except Exception as err:
                        logger.debug("On-the-fly translation error for %s #%s field '%s': %s", entity_type, eid, field, err)

    if new_translations_to_add:
        try:
            for rec in new_translations_to_add:
                session.add(rec)
            session.commit()
            logger.info("Auto-healed and persisted %d missing translations for %s", len(new_translations_to_add), entity_type)
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

    found_fields = set()
    for t in translations:
        if t.field_name in fields and t.translated_text:
            data[t.field_name] = t.translated_text
            found_fields.add(t.field_name)

    # Self-heal any missing fields
    missing_fields = [f for f in fields if f not in found_fields]
    if missing_fields:
        new_recs = []
        for field in missing_fields:
            clean_source = str(data.get(field) or "").strip()
            if not clean_source:
                continue
            is_name = field in name_fields_set
            try:
                if is_name:
                    from app.services.translation.transliteration import transliterate_name
                    trans_val = transliterate_name(clean_source, lang_code)
                else:
                    from app.services.translation.service import translate_batch_google_sync
                    batch_res = translate_batch_google_sync([clean_source], lang_code)
                    trans_val = batch_res[0] if batch_res else clean_source

                if trans_val and trans_val != clean_source:
                    data[field] = trans_val
                    from app.services.translation.manager import compute_hash
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
                    new_recs.append(new_rec)
            except Exception as err:
                logger.debug("On-the-fly dict translation error for %s #%s field '%s': %s", entity_type, entity_id, field, err)

        if new_recs:
            try:
                for rec in new_recs:
                    session.add(rec)
                session.commit()
            except Exception:
                session.rollback()

    return data

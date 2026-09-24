from __future__ import annotations

from typing import Any, Callable
from sqlalchemy.orm import Session
from app.models.translation import EntityTranslation


def overlay_entity_translations(
    session: Session,
    entities: list[Any],
    entity_type: str,
    id_getter: Callable[[Any], Any],
    fields: list[str],
    language: str | None,
) -> list[Any]:
    """Overlay pre-translated fields onto model instances or dicts in a single batch query.

    If language is 'en', None, or unsupported, returns entities unmodified.
    If a translation for a given field is missing or pending, the original English text is preserved.
    """
    if not language or language.lower().startswith("en") or not entities:
        return entities

    lang_code = "gu" if language.lower().startswith("gu") else "hi" if language.lower().startswith("hi") else None
    if not lang_code:
        return entities

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
) -> dict[str, Any]:
    """Helper to overlay translations on a single dictionary response object."""
    if not language or language.lower().startswith("en") or not data:
        return data

    lang_code = "gu" if language.lower().startswith("gu") else "hi" if language.lower().startswith("hi") else None
    if not lang_code:
        return data

    translations = session.query(EntityTranslation).filter(
        EntityTranslation.entity_type == entity_type,
        EntityTranslation.entity_id == str(entity_id),
        EntityTranslation.language == lang_code,
        EntityTranslation.status == "done",
    ).all()

    for t in translations:
        if t.field_name in fields and t.translated_text:
            data[t.field_name] = t.translated_text

    return data

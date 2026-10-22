from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.crud.alerts import get_user_language, list_user_alerts, mark_user_alert_read
from app.services.translation.overlay import overlay_entity_translations


def list_alerts(
    session: Session,
    user_id: str,
    offset: int,
    limit: int,
    language: str | None,
) -> list[dict[str, Any]]:
    alerts = list_user_alerts(session, user_id, offset, min(limit, 100))
    result = [
        {
            "id": alert.id,
            "prediction_id": alert.prediction_id,
            "kind": alert.kind,
            "severity": alert.severity,
            "title": alert.title,
            "body": alert.body,
            "is_read": alert.is_read,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
        }
        for alert in alerts
    ]

    language = language or get_user_language(session, user_id)
    overlay_entity_translations(
        session,
        result,
        "alert",
        lambda item: item["id"],
        ["title", "body"],
        language,
    )
    return result


def mark_alert_read(session: Session, user_id: str, alert_id: int) -> None:
    mark_user_alert_read(session, user_id, alert_id)

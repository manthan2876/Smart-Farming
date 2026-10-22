from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Alert, User


def list_user_alerts(
    session: Session,
    user_id: str,
    offset: int,
    limit: int,
) -> list[Alert]:
    return (
        session.query(Alert)
        .filter(Alert.user_id == user_id)
        .order_by(Alert.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_user_language(session: Session, user_id: str) -> str | None:
    user = session.get(User, user_id)
    return user.language if user else None


def mark_user_alert_read(session: Session, user_id: str, alert_id: int) -> bool:
    alert = (
        session.query(Alert)
        .filter(Alert.id == alert_id, Alert.user_id == user_id)
        .first()
    )
    if alert is None:
        return False

    alert.is_read = True
    session.commit()
    return True

from __future__ import annotations
from typing import Any
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core import get_session
from app.models import Alert
from app.services.translation.overlay import overlay_entity_translations

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("")
async def get_alerts(
    request: Request,
    offset: int = 0,
    limit: int = 20,
    lang: str | None = None,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[dict[str, Any]]:
    alerts = (
        session.query(Alert)
        .filter(Alert.user_id == user_id)
        .order_by(Alert.created_at.desc())
        .offset(offset)
        .limit(min(limit, 100))
        .all()
    )
    res = [
        {
            "id": a.id,
            "prediction_id": a.prediction_id,
            "kind": a.kind,
            "severity": a.severity,
            "title": a.title,
            "body": a.body,
            "is_read": a.is_read,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in alerts
    ]
    req_lang = lang or request.headers.get("accept-language")
    overlay_entity_translations(session, res, "alert", lambda x: x["id"], ["title", "body"], req_lang)
    return res


@router.post("/{alert_id}/read")
async def mark_read(
    alert_id: int, user_id: str = Depends(get_current_user), session: Session = Depends(get_session)
) -> dict[str, str]:
    alert = session.query(Alert).filter(Alert.id == alert_id, Alert.user_id == user_id).first()
    if alert:
        alert.is_read = True
        session.commit()
    return {"status": "ok"}

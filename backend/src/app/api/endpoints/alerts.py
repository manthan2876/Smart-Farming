from __future__ import annotations
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core import get_session
from app.models import Alert

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("")
async def get_alerts(
    user_id: str = Depends(get_current_user), session: Session = Depends(get_session)
) -> list[dict[str, Any]]:
    alerts = session.query(Alert).filter(Alert.user_id == user_id).order_by(Alert.created_at.desc()).limit(20).all()
    return [
        {
            "id": a.id,
            "prediction_id": a.prediction_id,
            "kind": a.kind,
            "severity": a.severity,
            "title": a.title,
            "body": a.body,
            "is_read": a.is_read,
            "created_at": a.created_at.isoformat()
        }
        for a in alerts
    ]

@router.post("/{alert_id}/read")
async def mark_read(
    alert_id: int, user_id: str = Depends(get_current_user), session: Session = Depends(get_session)
) -> dict[str, str]:
    alert = session.query(Alert).filter(Alert.id == alert_id, Alert.user_id == user_id).first()
    if alert:
        alert.is_read = True
        session.commit()
    return {"status": "ok"}

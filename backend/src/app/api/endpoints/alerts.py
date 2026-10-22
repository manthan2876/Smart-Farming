from __future__ import annotations

import logging
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.api.deps import get_current_user
from app.core import get_session
from app.schemas.alert import AlertReadResponse, AlertResponse
from app.services.alerts import list_alerts, mark_alert_read

router = APIRouter(prefix="/alerts", tags=["alerts"])
logger = logging.getLogger("smart-farming.api.alerts")

@router.get("", response_model=list[AlertResponse])
def get_alerts(
    request: Request,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    lang: str | None = None,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[dict[str, Any]]:
    try:
        requested_language = lang or request.headers.get("accept-language")
        return list_alerts(session, user_id, offset, limit, requested_language)
    except SQLAlchemyError as exc:
        logger.exception("Database error while listing alerts for user %s", user_id)
        raise HTTPException(status_code=503, detail="Unable to load alerts.") from exc


@router.post("/{alert_id}/read", response_model=AlertReadResponse)
def mark_read(
    alert_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, str]:
    try:
        mark_alert_read(session, user_id, alert_id)
    except SQLAlchemyError as exc:
        logger.exception(
            "Database error while marking alert %s read for user %s",
            alert_id,
            user_id,
        )
        raise HTTPException(status_code=503, detail="Unable to update alert.") from exc
    return {"status": "ok"}

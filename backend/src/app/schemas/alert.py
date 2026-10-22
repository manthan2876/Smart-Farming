from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    prediction_id: int | None = None
    kind: str
    severity: str
    title: str
    body: str
    is_read: bool
    created_at: datetime | None = None


class AlertReadResponse(BaseModel):
    status: str

from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class HealthResponse(BaseModel):
    status: str
    service: str

class QueueHealthResponse(BaseModel):
    status: str
    service: str
    mode: str
    redis_connected: bool
    pending_jobs: int = 0
    worker_healthy: bool = True
    details: dict[str, Any] = Field(default_factory=dict)

class ErrorResponse(BaseModel):
    detail: str
    status: str | None = None
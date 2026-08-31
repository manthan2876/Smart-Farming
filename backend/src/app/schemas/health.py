from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class HealthResponse(BaseModel):
    status: str
    service: str

class ErrorResponse(BaseModel):
    detail: str
    status: str | None = None
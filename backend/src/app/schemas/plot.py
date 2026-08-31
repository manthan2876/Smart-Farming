from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class PlotResponse(BaseModel):
    id: int
    name: str | None
    crop: str | None
    area_acres: float | None
    status: str | None


class PlotRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    crop: str = Field(min_length=1, max_length=100)
    area_acres: float = Field(ge=0, le=1_000_000)
    status: str = Field(min_length=1, max_length=20)
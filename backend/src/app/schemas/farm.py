from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class PlotResponse(BaseModel):
    id: int
    name: str
    crop: str | None
    area_acres: float | None
    status: str

class FarmResponse(BaseModel):
    id: int
    name: str | None
    location: str | None
    area_acres: float | None
    latitude: float | None
    longitude: float | None
    crop_history: list[str]
    plots: list[PlotResponse] = []


class FarmRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    location: str = Field(min_length=1, max_length=300)
    area_acres: float = Field(ge=0, le=1_000_000)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    crop_history: list[str] = Field(default_factory=list, max_length=50)
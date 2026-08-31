from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    location: str = Field(default="Unknown")
    lat: float = Field(default=52.2297, ge=-90, le=90)
    lon: float = Field(default=21.0122, ge=-180, le=180)
    language: str = Field(default="English", min_length=1, max_length=32)

class PredictionResponse(BaseModel):
    prediction_id: int | None = None
    request_id: str
    user: dict[str, Any]
    image: dict[str, Any]
    crop: dict[str, Any]
    disease: dict[str, Any]
    severity: dict[str, Any]
    pests: list[dict[str, Any]]
    pest_classification: dict[str, Any]
    weather: dict[str, Any]
    recommendation: dict[str, Any]
    notes: list[str]
    status: dict[str, str]
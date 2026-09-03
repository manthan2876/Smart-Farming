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
    request_id: str | None = None
    user: dict[str, Any] | None = None
    image: dict[str, Any] | None = None
    crop: dict[str, Any] | None = None
    disease: dict[str, Any] | None = None
    severity: dict[str, Any] | None = None
    pests: list[dict[str, Any]] | None = None
    pest_classification: dict[str, Any] | None = None
    weather: dict[str, Any] | None = None
    recommendation: dict[str, Any] | None = None
    notes: list[str] | None = None
    status: dict[str, Any] | None = None
    error: str | None = None
    expert_review_data: dict[str, Any] | None = None
    historical_images: list[dict[str, str]] | None = None
    follow_up: dict[str, Any] | None = None
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    location: str = Field(default="Unknown")
    lat: float | None = Field(default=None, ge=-90, le=90)
    lon: float | None = Field(default=None, ge=-180, le=180)
    language: str = Field(default="English", min_length=1, max_length=32)

class PredictionImageResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    raw_path: str | None = None
    processed_path: str | None = None
    raw_url: str | None = None
    processed_url: str | None = None
    quality_score: float | None = None
    leaf_detected: bool | None = None


class PredictionLabelResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    label: str | None = None
    confidence: float | None = None
    model_used: str | None = None


class PredictionSeverityResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    percent: float | None = None
    bucket: str | None = None


class PredictionWeatherResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    temperature_celsius: float | None = None
    humidity_percent: float | None = None
    condition: str | None = None
    status: str | None = None


class PredictionRecommendationResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    immediate_action: str | None = None
    treatment: str | None = None
    prevention: str | None = None
    monitoring: str | None = None
    safety_disclaimer: str | None = None


class PredictionExpertReviewResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    decision: str | None = None
    corrected_disease: str | None = None
    corrected_severity: float | None = None
    farmer_guidance: str | None = None
    status: str | None = None


class PredictionHistoricalImageResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    created_at: str | None = None
    disease: str | None = None
    severity_pct: float | None = None
    severity_bucket: str | None = None
    raw_path: str | None = None
    processed_path: str | None = None
    raw_url: str | None = None
    processed_url: str | None = None


class PredictionStatusResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    pipeline: str | None = None
    preprocessing: str | None = None
    expert_review: str | None = None


class PredictionResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    prediction_id: int | None = None
    id: int | None = None
    created_at: str | None = None
    job_id: str | None = None
    request_id: str | None = None
    user: dict[str, Any] | None = None
    image: PredictionImageResponse | None = None
    crop: PredictionLabelResponse | None = None
    disease: PredictionLabelResponse | None = None
    severity: PredictionSeverityResponse | None = None
    pests: list[PredictionLabelResponse] | None = None
    pest_classification: dict[str, Any] | None = None
    weather: PredictionWeatherResponse | None = None
    recommendation: PredictionRecommendationResponse | str | None = None
    notes: list[str] | None = None
    status: PredictionStatusResponse | str | None = None
    error: str | None = None
    stages: dict[str, Any] | None = None
    schema_version: str | None = None
    provenance: dict[str, Any] | None = None
    total_duration_ms: int | None = None
    expert_review_data: PredictionExpertReviewResponse | None = None
    historical_images: list[PredictionHistoricalImageResponse] | None = None
    follow_up: PredictionResponse | None = None
    translations: dict[str, PredictionRecommendationResponse] | None = None
    treatment_progress: dict[str, Any] | None = None
    farm: dict[str, Any] | None = None
    plot: dict[str, Any] | None = None

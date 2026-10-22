from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class WeatherResponse(BaseModel):
    temperature_celsius: float | None = None
    humidity_percent: float | None = None
    condition: str | None = None
    wind_speed_mps: float | None = None
    pressure_hpa: float | None = None
    cloudiness_percent: float | None = None
    advisory: str | None = None
    translated_advisory: str | None = None
    translations: dict[str, str] = Field(default_factory=dict)
    cached: bool | None = None
    timestamp: float | None = None


class WeatherTranslationRequest(BaseModel):
    text: str
    target_language: str


class WeatherTranslationResponse(BaseModel):
    translated_text: str
    language: str


class TTSRequest(BaseModel):
    text: str
    language: str | None = "English"


class TTSResponse(BaseModel):
    audioContent: str
    format: str
    cached: bool


class DatasetCropCount(BaseModel):
    crop: str
    count: int


class DatasetStatusCount(BaseModel):
    pending_review: int
    added_to_dataset: int


class DatasetSummaryResponse(BaseModel):
    total: int
    expert_overridden: int
    farmer_confirmed: int
    by_status: DatasetStatusCount
    by_crop: list[DatasetCropCount]


class AdminConfigResponse(BaseModel):
    crop_routing_threshold: float
    expert_escalation_cutoff: float


class AdminModelHealthItem(BaseModel):
    status: Literal["ok", "missing"]
    model_file: str
    model_exists: bool
    labels_file: str | None
    labels_exists: bool
    active_version: str | None
    val_acc: float | None
    test_acc: float | None
    trained_at: str | None


class AdminModelHealthResponse(BaseModel):
    overall_status: Literal["healthy", "degraded"]
    checked_at: str
    models: dict[str, AdminModelHealthItem]


class AdminBlobPurgeResponse(BaseModel):
    status: Literal["success", "dry_run"]
    deleted_files: int | None = None
    local_deleted: int | None = None
    cloud_deleted: int | None = None
    supabase_deleted: int | None = None
    s3_deleted: int | None = None
    cloud_error: str | None = None
    unreferenced_files_count: int | None = None
    local_unreferenced_count: int | None = None
    cloud_unreferenced_count: int | None = None
    supabase_unreferenced_count: int | None = None
    s3_unreferenced_count: int | None = None
    files: list[str] | None = None
    local_files: list[str] | None = None
    cloud_files: list[str] | None = None


class AdminPurgeCounts(BaseModel):
    dataset_candidates: int
    expert_reviews: int
    recommendations: int
    feedback: int
    alerts: int
    predictions: int
    images: int


class AdminDatabasePurgeResponse(BaseModel):
    status: Literal["success", "dry_run"]
    message: str
    counts: AdminPurgeCounts | None = None


class PredictionTranslationResponse(BaseModel):
    prediction_id: int
    language: str
    cached: bool
    recommendation: dict[str, str]
    expert_guidance: str | None = None
    translations: dict[str, dict[str, str]] | None = None
    translation_status: str | None = None
    warning: str | None = None

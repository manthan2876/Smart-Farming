from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class AdminFailureMetrics(BaseModel):
    total_failed: int
    failure_rate: float


class AdminProcessingDuration(BaseModel):
    avg_ms: int
    p95_ms: int
    sample_count: int


class AdminFallbackMetrics(BaseModel):
    recommendation_fallbacks: int
    weather_fallbacks: int


class AdminExpertMetrics(BaseModel):
    total_reviews: int
    approved: int
    overrides: int
    pending: int
    validated_accuracy: float | None


class AdminConfidenceDrift(BaseModel):
    avg_disease_confidence_7d: float | None
    avg_disease_confidence_30d: float | None
    low_confidence_rate_7d: float | None
    predictions_last_7d: int
    low_confidence_last_7d: int
    retraining_candidates: int
    expert_correction_rate: float | None
    confidence_threshold: float


class AdminDiseaseCount(BaseModel):
    name: str
    value: int


class AdminConfidenceBucket(BaseModel):
    name: str
    count: int


class AdminMetricsResponse(BaseModel):
    total_users: int
    total_scans: int
    completed_scans: int
    accuracy: float
    farmer_reported_accuracy: float
    expert_audit_accuracy: float | None
    accuracy_source: Literal["expert_audit", "farmer_feedback"]
    queue_depth: int
    failures: AdminFailureMetrics
    processing_duration: AdminProcessingDuration
    fallbacks: AdminFallbackMetrics
    expert_metrics: AdminExpertMetrics
    disease_distribution: list[AdminDiseaseCount]
    confidence_histogram: list[AdminConfidenceBucket]
    drift: AdminConfidenceDrift


class AdminUserResponse(BaseModel):
    id: str
    name: str
    email: str | None
    phone: str | None
    role: Literal["farmer", "expert", "admin"]
    language: str | None
    created_at: str | None
    deleted_at: str | None
    scan_count: int
    farm_name: str | None
    farm_location: str | None


class AdminUsersResponse(BaseModel):
    total: int
    users: list[AdminUserResponse]


class AdminRoleUpdateResponse(BaseModel):
    status: Literal["success"]
    user_id: str
    old_role: str
    new_role: str
    reason: str | None


class AdminUserUpdateResponse(BaseModel):
    status: Literal["success"]
    user_id: str
    name: str
    phone: str | None
    role: str
    old_role: str
    new_role: str
    reason: str | None


class AdminFeedbackResponse(BaseModel):
    id: int
    prediction_id: int
    crop: str | None
    disease: str | None
    is_correct: bool
    farmer_note: str | None
    review_status: str | None
    review_decision: str | None
    reviewer_id: str | None
    reviewer_note: str | None
    reviewed_at: str | None
    created_at: str


class FeedbackReviewResponse(BaseModel):
    status: Literal["success"]
    feedback_id: int
    review_status: str
    corrected_label: str | None


class ModelRollbackResponse(BaseModel):
    status: Literal["rolled_back"]
    model_key: str
    previous_version: str | None
    active_version: str
    storage: Literal["postgresql_database"]


class WeatherRiskTriggerResponse(BaseModel):
    status: Literal["success"]
    result: str

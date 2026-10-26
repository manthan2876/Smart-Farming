from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ExpertQueueItemResponse(BaseModel):
    review_id: int
    prediction_id: int
    status: str
    crop: str | None
    disease: str | None
    disease_conf: float | None
    severity_pct: float | None
    claimed_by: str | None = None
    claimed_at: str | None = None
    created_at: str | None = None


class ExpertReviewDetailResponse(BaseModel):
    review_id: int
    prediction_id: int
    status: str
    decision: str | None
    corrected_disease: str | None
    farmer_guidance: str | None
    internal_note: str | None
    raw_path: str | None
    processed_path: str | None
    raw_url: str | None = None
    processed_url: str | None = None
    crop: str | None
    disease: str | None
    disease_conf: float | None
    severity_pct: float | None
    created_at: str | None


class ExpertReviewSubmissionRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    action: str | None = None
    decision: str | None = None
    corrected_disease: str | None = None
    corrected_severity: str | float | None = None
    pest_verified: bool | None = None
    farmer_guidance: str | None = None
    internal_note: str | None = None
    add_to_retraining: bool | None = None


class ExpertReviewSubmissionResponse(BaseModel):
    status: str
    review_id: int

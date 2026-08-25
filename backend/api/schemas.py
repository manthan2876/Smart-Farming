from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    location: str = Field(default="Unknown")
    lat: float = Field(default=52.2297, ge=-90, le=90)
    lon: float = Field(default=21.0122, ge=-180, le=180)
    language: str = Field(default="English", min_length=1, max_length=32)


class HealthResponse(BaseModel):
    status: str
    service: str


class CropListResponse(BaseModel):
    crops: list[str]


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


class FeedbackRequest(BaseModel):
    prediction_id: int = Field(gt=0)
    is_correct: bool
    farmer_note: str | None = Field(default=None, max_length=2000)


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=8, max_length=128)
    phone: str | None = Field(default=None, max_length=40)
    email: str | None = Field(default=None, max_length=320)
    location: str | None = Field(default=None, max_length=300)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    language: str = Field(default="English", min_length=1, max_length=32)
    crop_history: list[str] = Field(default_factory=list, max_length=50)


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=1, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class ProfileUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    location: str | None = Field(default=None, max_length=300)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    language: str | None = Field(default=None, min_length=1, max_length=32)
    crop_history: list[str] | None = Field(default=None, max_length=50)


class ProfileResponse(BaseModel):
    id: str
    name: str | None
    phone: str | None
    email: str | None
    language: str
    role: str
    location: str | None
    latitude: float | None
    longitude: float | None
    crop_history: list[str]


class AuthResponse(BaseModel):
    tokens: dict[str, str | int]
    user: ProfileResponse


class FeedbackResponse(BaseModel):
    id: int
    prediction_id: int
    is_correct: bool
    farmer_note: str | None


class ErrorResponse(BaseModel):
    detail: str
    status: str | None = None

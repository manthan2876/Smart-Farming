from __future__ import annotations

from pydantic import BaseModel, Field

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
    farm_name: str | None = Field(default=None, max_length=200)
    farm_area_acres: float | None = Field(default=None, ge=0, le=1_000_000)

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
    farm_name: str | None = Field(default=None, max_length=200)
    farm_area_acres: float | None = Field(default=None, ge=0, le=1_000_000)


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
    farm_name: str | None = None
    farm_area_acres: float | None = None


class AuthResponse(BaseModel):
    tokens: dict[str, str | int]
    user: ProfileResponse
from app.api.deps import (
    get_current_user,
    create_token_pair,
    decode_token,
    hash_password,
    verify_password,
)
from app.api.endpoints.weather import _json_safe, router as weather_router
from app.api.endpoints.auth import get_session, router as auth_router
from app.api.endpoints.predict import router as predict_router, _public_result
from app.api.endpoints.history import router as history_router
from app.api.endpoints.feedback import router as feedback_router
from app.api.endpoints.crops import router as crops_router
from app.api.endpoints.health import router as health_router
from app.api.endpoints.adminMatrix import router as admin_router

__all__ = [
    "get_current_user",
    "create_token_pair",
    "decode_token",
    "hash_password",
    "verify_password",
    "_json_safe",
    "_public_result",
    "get_session",
    "auth_router",
    "predict_router",
    "history_router",
    "feedback_router",
    "weather_router",
    "crops_router",
    "health_router",
    "admin_router",
]
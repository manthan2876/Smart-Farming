"""API Routers for the unified AI service."""
from .vision import router as vision_router
from .translation import router as translation_router
from .advisory import router as advisory_router
from .tts import router as tts_router

__all__ = ["vision_router", "translation_router", "advisory_router", "tts_router"]


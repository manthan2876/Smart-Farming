"""API Routers for the unified AI service."""

try:
    from .vision import router as vision_router
except Exception:
    vision_router = None

try:
    from .translation import router as translation_router
except Exception:
    translation_router = None

try:
    from .advisory import router as advisory_router
except Exception:
    advisory_router = None

try:
    from .tts import router as tts_router
except Exception:
    tts_router = None

__all__ = ["vision_router", "translation_router", "advisory_router", "tts_router"]


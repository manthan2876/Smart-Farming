"""
ai_service/core/config.py — Global configuration and settings for the unified AI microservice.
"""

from __future__ import annotations

import os
from pathlib import Path
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings
import torch

AI_SERVICE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = AI_SERVICE_DIR.parent


def _detect_device() -> str:
    if os.getenv("FORCE_CPU", "").lower() in ("true", "1"):
        return "cpu"
    if torch.cuda.is_available():
        try:
            torch.zeros(1, device="cuda")
            return "cuda"
        except Exception:
            return "cpu"
    return "cpu"


class Settings(BaseSettings):
    SERVICE_NAME: str = "Smart Farming Unified AI Service"
    VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1")

    # Hardware & Threads
    DEVICE: str = _detect_device()
    CPU_THREADS: int = int(os.getenv("CPU_THREADS", str(min(os.cpu_count() or 2, 4))))

    # Security
    GATEWAY_SECRET: str = os.getenv("GATEWAY_SECRET", "")
    ALLOW_ALL_ORIGINS: bool = True

    # Cloud LLM APIs for fast advisory generation (Groq or Gemini)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Paths
    KB_PATH: Path = AI_SERVICE_DIR / "advisory_kb.json"
    CONFIG_YAML_PATH: Path = AI_SERVICE_DIR / "config.yaml"

    # Vision Models Directory
    MODELS_DIR: Path = AI_SERVICE_DIR / "models"

    # Caches
    CACHE_DIR: Path = Path(os.getenv("CACHE_DIR", str(AI_SERVICE_DIR / "cache")))

    def get_models_dir(self) -> Path:
        return self.MODELS_DIR

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

# Configure PyTorch CPU threading
if settings.DEVICE == "cpu":
    torch.set_num_threads(settings.CPU_THREADS)

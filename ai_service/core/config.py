"""
ai_service/core/config.py — Global configuration and settings for the unified AI microservice.
"""

from __future__ import annotations

import os
from pathlib import Path
try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic import BaseModel as BaseSettings
    except ImportError:
        class BaseSettings:  # type: ignore
            pass
try:
    import torch
except Exception:
    torch = None

AI_SERVICE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = AI_SERVICE_DIR.parent


def _detect_device() -> str:
    if os.getenv("FORCE_CPU", "").lower() in ("true", "1"):
        return "cpu"
    # On Hugging Face ZeroGPU, dynamic CUDA allocation only activates for Gradio UI callbacks.
    # REST API endpoints (/vision, /translation, /advisory) must run on CPU to avoid CUDA resource locks.
    if os.getenv("SPACES_ZERO_GPU"):
        return "cpu"
    if torch and hasattr(torch, "cuda") and torch.cuda.is_available():
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

    # Advisory LLM Engine (Default False for instant verified ICAR/KVK facts, or Optional Groq/Local LLM)
    USE_LOCAL_LLM: bool = os.getenv("USE_LOCAL_LLM", "false").lower() in ("true", "1")
    LOCAL_LLM_MODEL: str = os.getenv("LOCAL_LLM_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Flagship Translation Model (Plan default: dist-200M for sub-second CPU response)
    INDICTRANS_MODEL: str = os.getenv("INDICTRANS_MODEL", "ai4bharat/indictrans2-en-indic-dist-200M")

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
if torch and hasattr(torch, "set_num_threads") and settings.DEVICE == "cpu":
    torch.set_num_threads(settings.CPU_THREADS)

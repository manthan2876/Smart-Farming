from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    SECRET_KEY: str = Field(default="dev-secret-key-change-me") 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = Field(default="sqlite:///./dev_database.db")
    REDIS_URL: str = "redis://127.0.0.1:6379"
    REQUIRE_REDIS: bool = False
    UPLOAD_MAX_BYTES: int = 10 * 1024 * 1024
    CROP_CONFIDENCE_THRESHOLD: float = 0.7
    DISEASE_CONFIDENCE_THRESHOLD: float = 0.7
    BACKEND_ROOT: Path = BACKEND_ROOT
    CONFIG_PATH: Path = BACKEND_ROOT / "config.yaml"
    DATA_ROOT: Path = BACKEND_ROOT / "data"
    UPLOAD_ROOT: Path = DATA_ROOT / "uploads"
    PROCESSED_ROOT: Path = DATA_ROOT / "processed"
    AUDIO_ROOT: Path = DATA_ROOT / "audio"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
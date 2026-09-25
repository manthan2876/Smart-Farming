from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(BACKEND_ROOT / ".env")

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
    GOOGLE_TTS_API_KEY: str = Field(default="")
    GOOGLE_TRANSLATION_API_KEY: str = Field(default="")
    GEMINI_API_KEY: str = Field(default="")

    # Model Inference Server (Server 2)
    MODEL_SERVER_URL: str = Field(default="http://127.0.0.1:8001")
    MODEL_SERVER_TIMEOUT: int = Field(default=60)

    # Storage (AWS S3 & Google Cloud Storage)
    STORAGE_BACKEND: str = Field(default="local")
    AWS_ACCESS_KEY_ID: str | None = Field(default=None)
    AWS_SECRET_ACCESS_KEY: str | None = Field(default=None)
    AWS_REGION: str = Field(default="us-east-1")
    AWS_S3_BUCKET: str = Field(default="smart-farming-data")
    AWS_ENDPOINT_URL: str | None = Field(default=None)
    STORAGE_ENDPOINT_URL: str | None = Field(default=None)
    GCS_BUCKET: str | None = Field(default=None)
    S3_PRESIGNED_EXPIRY_SECONDS: int = 900

    # Upstash Serverless Redis REST
    UPSTASH_REDIS_REST_URL: str | None = Field(default=None)
    UPSTASH_REDIS_REST_TOKEN: str | None = Field(default=None)

    # Environment and Security
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    JWT_SECRET_KEY: str = Field(default="dev-secret-key-change-me")

    model_config = SettingsConfigDict(env_file=BACKEND_ROOT / ".env", extra="ignore")

settings = Settings()

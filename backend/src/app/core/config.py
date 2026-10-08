from pathlib import Path
from urllib.parse import urlparse

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(BACKEND_ROOT / ".env")

class Settings(BaseSettings):
    SECRET_KEY: str = Field(default="dev-secret-key-change-me") 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = Field(default="sqlite:///./dev_database.db")
    PROD_DATABASE_URL: str | None = Field(default=None)
    REQUIRE_REDIS: bool = False
    LOCAL_REDIS_URL: str = "redis://localhost:6379"
    UPSTASH_REDIS_URL: str | None = Field(default=None)
    REDIS_URL: str = ""
    ARQ_POLL_DELAY: float | None = Field(default=None)
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

    # Geographic Defaults (Indian agricultural reference region)
    DEFAULT_LAT: float = Field(default=21.7645)
    DEFAULT_LON: float = Field(default=72.1519)
    DEFAULT_LOCATION: str = Field(default="Gujarat, India")

    # Model Inference Server (Server 2)
    MODEL_SERVER_URL: str = Field(default="http://127.0.0.1:8001")
    MODEL_SERVER_TIMEOUT: int = Field(default=120)

    # Storage (AWS S3)
    STORAGE_BACKEND: str = Field(default="s3")
    AWS_ACCESS_KEY_ID: str | None = Field(default=None)
    AWS_SECRET_ACCESS_KEY: str | None = Field(default=None)
    AWS_REGION: str = Field(default="us-east-1")
    AWS_S3_BUCKET: str = Field(default="smart-farming-data")
    AWS_ENDPOINT_URL: str | None = Field(default=None)
    STORAGE_ENDPOINT_URL: str | None = Field(default=None)
    S3_PRESIGNED_EXPIRY_SECONDS: int = 900

    # Upstash Serverless Redis REST
    UPSTASH_REDIS_REST_URL: str | None = Field(default=None)
    UPSTASH_REDIS_REST_TOKEN: str | None = Field(default=None)

    # Upstash QStash (Serverless Scheduled Crons & Webhooks)
    QSTASH_REGION: str = Field(default="US_EAST_1")
    QSTASH_URL: str | None = Field(default=None)
    QSTASH_TOKEN: str | None = Field(default=None)
    QSTASH_CURRENT_SIGNING_KEY: str | None = Field(default=None)
    QSTASH_NEXT_SIGNING_KEY: str | None = Field(default=None)

    EU_CENTRAL_1_QSTASH_URL: str | None = Field(default=None)
    EU_CENTRAL_1_QSTASH_TOKEN: str | None = Field(default=None)
    EU_CENTRAL_1_QSTASH_CURRENT_SIGNING_KEY: str | None = Field(default=None)
    EU_CENTRAL_1_QSTASH_NEXT_SIGNING_KEY: str | None = Field(default=None)

    US_EAST_1_QSTASH_URL: str | None = Field(default=None)
    US_EAST_1_QSTASH_TOKEN: str | None = Field(default=None)
    US_EAST_1_QSTASH_CURRENT_SIGNING_KEY: str | None = Field(default=None)
    US_EAST_1_QSTASH_NEXT_SIGNING_KEY: str | None = Field(default=None)

    CRON_SECRET: str | None = Field(default=None)

    # Environment and Security
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    JWT_SECRET_KEY: str = Field(default="dev-secret-key-change-me")

    # Email / SMTP Configuration
    SMTP_HOST: str | None = Field(default=None)
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str | None = Field(default=None)
    SMTP_PASSWORD: str | None = Field(default=None)
    SMTP_TLS: bool = Field(default=True)
    SMTP_SSL: bool = Field(default=False)
    EMAILS_FROM_EMAIL: str | None = Field(default=None)
    EMAILS_FROM_NAME: str = Field(default="Smart Farming Support")
    FRONTEND_URL: str = Field(default="http://localhost:5173")

    @property
    def primary_qstash_url(self) -> str:
        url = self.QSTASH_URL
        if not url:
            if self.QSTASH_REGION.upper() == "US_EAST_1" and self.US_EAST_1_QSTASH_URL:
                url = self.US_EAST_1_QSTASH_URL
            elif self.QSTASH_REGION.upper() == "EU_CENTRAL_1" and self.EU_CENTRAL_1_QSTASH_URL:
                url = self.EU_CENTRAL_1_QSTASH_URL
            elif self.US_EAST_1_QSTASH_URL:
                url = self.US_EAST_1_QSTASH_URL
            elif self.EU_CENTRAL_1_QSTASH_URL:
                url = self.EU_CENTRAL_1_QSTASH_URL
            else:
                url = "https://qstash.upstash.io/v2"
        clean = (url or "").rstrip("/")
        if not clean.endswith("/v2"):
            clean = f"{clean}/v2"
        return clean

    @property
    def primary_qstash_token(self) -> str:
        if self.QSTASH_TOKEN:
            return self.QSTASH_TOKEN
        if self.QSTASH_REGION.upper() == "US_EAST_1" and self.US_EAST_1_QSTASH_TOKEN:
            return self.US_EAST_1_QSTASH_TOKEN
        if self.QSTASH_REGION.upper() == "EU_CENTRAL_1" and self.EU_CENTRAL_1_QSTASH_TOKEN:
            return self.EU_CENTRAL_1_QSTASH_TOKEN
        if self.US_EAST_1_QSTASH_TOKEN:
            return self.US_EAST_1_QSTASH_TOKEN
        if self.EU_CENTRAL_1_QSTASH_TOKEN:
            return self.EU_CENTRAL_1_QSTASH_TOKEN
        return ""

    @property
    def all_qstash_signing_keys(self) -> list[str]:
        """Returns all configured QStash signing keys across primary and secondary regions."""
        keys = [
            self.QSTASH_CURRENT_SIGNING_KEY,
            self.QSTASH_NEXT_SIGNING_KEY,
            self.EU_CENTRAL_1_QSTASH_CURRENT_SIGNING_KEY,
            self.EU_CENTRAL_1_QSTASH_NEXT_SIGNING_KEY,
            self.US_EAST_1_QSTASH_CURRENT_SIGNING_KEY,
            self.US_EAST_1_QSTASH_NEXT_SIGNING_KEY,
        ]
        return [k.strip() for k in keys if k and k.strip()]

    @model_validator(mode="after")
    def resolve_redis_url(self) -> "Settings":
        # 1. Resolve Upstash Redis TLS DSN if not explicitly set
        if not self.UPSTASH_REDIS_URL and self.UPSTASH_REDIS_REST_URL and self.UPSTASH_REDIS_REST_TOKEN:
            host = urlparse(self.UPSTASH_REDIS_REST_URL).hostname
            if host:
                self.UPSTASH_REDIS_URL = f"rediss://default:{self.UPSTASH_REDIS_REST_TOKEN}@{host}:6379"

        # 2. Select active REDIS_URL based on REQUIRE_REDIS toggle:
        #    REQUIRE_REDIS=True  -> Local Docker Redis instance (LOCAL_REDIS_URL)
        #    REQUIRE_REDIS=False -> Upstash Cloud Redis instance (UPSTASH_REDIS_URL)
        if self.REQUIRE_REDIS:
            local_target = self.LOCAL_REDIS_URL or "redis://localhost:6379"
            if self.REDIS_URL and any(h in self.REDIS_URL for h in ("127.0.0.1", "localhost")):
                pass
            else:
                self.REDIS_URL = local_target
        else:
            if self.UPSTASH_REDIS_URL:
                self.REDIS_URL = self.UPSTASH_REDIS_URL
            elif self.REDIS_URL and not any(h in self.REDIS_URL for h in ("127.0.0.1", "localhost")):
                pass
            else:
                self.REDIS_URL = self.LOCAL_REDIS_URL or "redis://localhost:6379"

        return self

    model_config = SettingsConfigDict(env_file=BACKEND_ROOT / ".env", extra="ignore")

settings = Settings()

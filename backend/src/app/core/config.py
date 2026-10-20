from __future__ import annotations

import os
from pathlib import Path
from typing import Self
from urllib.parse import urlparse

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parents[3]

_env_file_name = os.getenv("ENV_FILE") or (".env.production" if os.getenv("ENVIRONMENT") == "production" else ".env")
_env_path = BACKEND_ROOT / _env_file_name
if _env_path.exists():
    load_dotenv(_env_path, override=True)
else:
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

    # Geographic Defaults (Indian agricultural reference region)
    DEFAULT_LAT: float = Field(default=21.7645)
    DEFAULT_LON: float = Field(default=72.1519)
    DEFAULT_LOCATION: str = Field(default="Gujarat, India")

    # Unified AI Microservice (Single Hugging Face Space URL)
    AI_SERVICE_URL: str = Field(default="https://maharsh8805-smart-farming-ai.hf.space")

    # Derived AI Service Subroute Endpoints (automatically derived from AI_SERVICE_URL)
    MODEL_SERVER_URL: str = Field(default="")
    MODEL_SERVER_TIMEOUT: int = Field(default=120)

    TRANSLATION_SERVER_URL: str = Field(default="")
    TRANSLATION_SERVER_TIMEOUT: float = Field(default=45.0)

    ADVISORY_SERVER_URL: str = Field(default="")
    ADVISORY_SERVER_TIMEOUT: float = Field(default=60.0)

    TTS_SERVER_URL: str = Field(default="")
    TTS_SERVER_TIMEOUT: float = Field(default=90.0)

    # AI Service API Authentication (Optional Bearer token)
    GATEWAY_API_KEY: str | None = Field(default=None)

    # Storage & Auth (Supabase Object Storage & Supabase Auth)
    STORAGE_BACKEND: str = Field(default="supabase")
    SUPABASE_URL: str = Field(default="")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(default="")
    SUPABASE_ANON_KEY: str = Field(default="")
    SUPABASE_JWT_SECRET: str | None = Field(default=None)
    SUPABASE_BUCKET: str = Field(default="smart-farming-data-dev")
    SUPABASE_SIGNED_URL_EXPIRY_SECONDS: int = Field(default=900)

    # Backward compatibility properties
    @property
    def AWS_S3_BUCKET(self) -> str:
        return self.SUPABASE_BUCKET

    @property
    def S3_PRESIGNED_EXPIRY_SECONDS(self) -> int:
        return self.SUPABASE_SIGNED_URL_EXPIRY_SECONDS

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

    # Email / SMTP Configuration (Managed via Supabase Custom SMTP; local SMTP fields are optional fallbacks)
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

    @model_validator(mode="after")
    def resolve_ai_service_urls(self) -> "Settings":
        """Single source of truth: all AI endpoints derive from AI_SERVICE_URL.
        
        Guarantees that individual endpoints (/vision, /translation, /advisory, /tts)
        are automatically derived from the single Hugging Face Space URL.
        Any stale separate URLs or legacy tunnels (e.g. trycloudflare.com, workers.dev,
        ngrok) are automatically overridden.
        """
        legacy_patterns = (
            "trycloudflare.com",
            "workers.dev",
            "ngrok",
            "ngrok-free.app",
            "ngrok.io",
        )

        def is_legacy(url: str | None) -> bool:
            if not url or not url.strip():
                return False
            lower = url.strip().lower()
            return any(pat in lower for pat in legacy_patterns)

        # Sanitize AI_SERVICE_URL if empty or pointing to legacy tunnel/worker
        if not self.AI_SERVICE_URL or is_legacy(self.AI_SERVICE_URL):
            self.AI_SERVICE_URL = "https://maharsh8805-smart-farming-ai.hf.space"

        base = self.AI_SERVICE_URL.rstrip("/")

        mapping = [
            ("MODEL_SERVER_URL", "/vision", ["/predict"]),
            ("TRANSLATION_SERVER_URL", "/translation", ["/translate"]),
            ("ADVISORY_SERVER_URL", "/advisory", ["/advise"]),
            ("TTS_SERVER_URL", "/tts", ["/synthesize", "/tts/synthesize"]),
        ]

        for field, subpath, strip_suffixes in mapping:
            val = (getattr(self, field, "") or "").strip()
            # If not explicitly set, legacy tunnel/gateway, in production, or matching default base:
            # Always derive directly from AI_SERVICE_URL
            if (
                not val
                or is_legacy(val)
                or self.ENVIRONMENT == "production"
                or not any(h in val for h in ("127.0.0.1", "localhost"))
            ):
                setattr(self, field, f"{base}{subpath}")
            else:
                clean_val = val.rstrip("/")
                for sfx in strip_suffixes:
                    if clean_val.endswith(sfx):
                        clean_val = clean_val[:-len(sfx)].rstrip("/")
                if clean_val.endswith(".hf.space"):
                    clean_val = f"{clean_val}{subpath}"
                setattr(self, field, clean_val)

        return self

    @model_validator(mode="after")
    def validate_security_config(self) -> Self:
        """Enforces strong JWT secret keys in production and staging environments."""
        insecure_keys = {
            "dev-secret-key-change-me",
            "change-this-development-secret-key-32-bytes",
            "replace_with_a_long_random_jwt_secret_key",
            "generate_strong_64_character_random_hex_key_for_production",
            "secret",
            "default",
        }
        env = (self.ENVIRONMENT or "development").strip().lower()
        if env in ("production", "staging"):
            key = (self.JWT_SECRET_KEY or "").strip()
            if not key or key in insecure_keys or len(key) < 32:
                raise ValueError(
                    f"FATAL: Insecure or default JWT_SECRET_KEY detected in '{env}' environment. "
                    "A unique random key of at least 32 characters must be configured."
                )
        return self

    model_config = SettingsConfigDict(
        env_file=(_env_path if _env_path.exists() else BACKEND_ROOT / ".env"),
        extra="ignore",
    )

settings = Settings()

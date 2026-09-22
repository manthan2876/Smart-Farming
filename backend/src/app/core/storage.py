from __future__ import annotations

import io
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from app.core.config import settings

logger = logging.getLogger("smart-farming.storage")


class StorageBackend(ABC):
    """Abstract interface for storing and retrieving prediction images and audio assets."""

    @abstractmethod
    def save(self, content: bytes, destination_key: str, content_type: str = "application/octet-stream") -> str:
        """Save binary content to destination_key. Returns normalized key."""
        pass

    @abstractmethod
    def get(self, key: str) -> bytes:
        """Retrieve binary content for the given key."""
        pass

    @abstractmethod
    def get_url(self, key: str, expires_in: int = 900) -> str:
        """Get an authorized download/view URL (presigned URL for S3, static path for local)."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete object at key. Returns True if deleted or did not exist."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if an object exists at key."""
        pass

    @abstractmethod
    def list_objects(self, prefix: str = "") -> list[str]:
        """List object keys under the given prefix."""
        pass


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage implementation."""

    def __init__(self, data_root: Path | None = None) -> None:
        self.data_root = (data_root or settings.DATA_ROOT).resolve()
        self.data_root.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, key: str) -> Path:
        clean_key = key.replace("\\", "/").strip("/")
        if clean_key.startswith("data/"):
            clean_key = clean_key[5:]
        target = (self.data_root / clean_key).resolve()
        try:
            target.relative_to(self.data_root)
        except ValueError as exc:
            raise ValueError(f"Path traversal detected: {key}") from exc
        return target

    def save(self, content: bytes, destination_key: str, content_type: str = "application/octet-stream") -> str:
        target = self._resolve_path(destination_key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        normalized = f"data/{target.relative_to(self.data_root).as_posix()}"
        return normalized

    def get(self, key: str) -> bytes:
        target = self._resolve_path(key)
        if not target.is_file():
            raise FileNotFoundError(f"Object not found: {key}")
        return target.read_bytes()

    def get_url(self, key: str, expires_in: int = 900) -> str:
        clean_key = key.replace("\\", "/").strip("/")
        if not clean_key.startswith("data/"):
            clean_key = f"data/{clean_key}"
        return f"/{clean_key}"

    def delete(self, key: str) -> bool:
        try:
            target = self._resolve_path(key)
            if target.is_file():
                target.unlink()
                return True
            return False
        except Exception as exc:
            logger.warning("Local delete error for %s: %s", key, exc)
            return False

    def exists(self, key: str) -> bool:
        try:
            target = self._resolve_path(key)
            return target.is_file()
        except Exception:
            return False

    def list_objects(self, prefix: str = "") -> list[str]:
        target_dir = self._resolve_path(prefix) if prefix else self.data_root
        if not target_dir.exists():
            return []
        if target_dir.is_file():
            return [f"data/{target_dir.relative_to(self.data_root).as_posix()}"]
        keys: list[str] = []
        for p in target_dir.rglob("*"):
            if p.is_file():
                keys.append(f"data/{p.relative_to(self.data_root).as_posix()}")
        return keys


class S3StorageBackend(StorageBackend):
    """AWS S3 storage implementation with AES256 encryption and secure presigned URLs."""

    def __init__(
        self,
        bucket_name: str | None = None,
        region: str | None = None,
        access_key_id: str | None = None,
        secret_access_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.bucket_name = bucket_name or settings.AWS_S3_BUCKET
        self.region = region or kwargs.get("region_name") or settings.AWS_REGION
        self.region_name = self.region
        self.access_key_id = access_key_id or kwargs.get("access_key") or settings.AWS_ACCESS_KEY_ID
        self.secret_access_key = secret_access_key or kwargs.get("secret_key") or settings.AWS_SECRET_ACCESS_KEY
        self._client: Any = None


    @property
    def client(self) -> Any:
        if self._client is None:
            import boto3
            from botocore.config import Config

            boto_config = Config(
                region_name=self.region,
                signature_version="s3v4",
                retries={"max_attempts": 3, "mode": "standard"},
            )
            kwargs: dict[str, Any] = {"config": boto_config}
            if self.access_key_id and self.secret_access_key:
                kwargs["aws_access_key_id"] = self.access_key_id
                kwargs["aws_secret_access_key"] = self.secret_access_key

            self._client = boto3.client("s3", **kwargs)
        return self._client

    def _normalize_key(self, key: str) -> str:
        clean = key.replace("\\", "/").strip("/")
        if clean.startswith("data/"):
            clean = clean[5:]
        return clean

    def save(self, content: bytes, destination_key: str, content_type: str = "application/octet-stream") -> str:
        key = self._normalize_key(destination_key)
        self.client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=content,
            ContentType=content_type,
            ServerSideEncryption="AES256",
        )
        return key

    def get(self, key: str) -> bytes:
        norm_key = self._normalize_key(key)
        resp = self.client.get_object(Bucket=self.bucket_name, Key=norm_key)
        return resp["Body"].read()

    def get_url(self, key: str, expires_in: int = 900) -> str:
        norm_key = self._normalize_key(key)
        url: str = self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": norm_key},
            ExpiresIn=expires_in,
        )
        return url

    def delete(self, key: str) -> bool:
        norm_key = self._normalize_key(key)
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=norm_key)
            return True
        except Exception as exc:
            logger.warning("S3 delete object failed for %s: %s", norm_key, exc)
            return False

    def exists(self, key: str) -> bool:
        norm_key = self._normalize_key(key)
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=norm_key)
            return True
        except Exception:
            return False

    def list_objects(self, prefix: str = "") -> list[str]:
        norm_prefix = self._normalize_key(prefix) if prefix else ""
        paginator = self.client.get_paginator("list_objects_v2")
        keys: list[str] = []
        for page in paginator.paginate(Bucket=self.bucket_name, Prefix=norm_prefix):
            for item in page.get("Contents", []):
                keys.append(item["Key"])
        return keys


_STORAGE_INSTANCE: StorageBackend | None = None


def get_storage() -> StorageBackend:
    """Singleton accessor for configured storage backend."""
    global _STORAGE_INSTANCE
    if _STORAGE_INSTANCE is None:
        backend_type = (settings.STORAGE_BACKEND or "local").lower()
        if backend_type == "s3":
            logger.info("Initializing S3StorageBackend for bucket: %s (%s)", settings.AWS_S3_BUCKET, settings.AWS_REGION)
            _STORAGE_INSTANCE = S3StorageBackend()
        else:
            logger.info("Initializing LocalStorageBackend at: %s", settings.DATA_ROOT)
            _STORAGE_INSTANCE = LocalStorageBackend()
    return _STORAGE_INSTANCE


def reset_storage() -> None:
    """Reset storage singleton (useful in test harnesses)."""
    global _STORAGE_INSTANCE
    _STORAGE_INSTANCE = None


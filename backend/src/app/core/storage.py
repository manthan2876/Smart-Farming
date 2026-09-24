from __future__ import annotations

import io
import time
from datetime import datetime, timezone
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


def purge_orphaned_blobs(
    session: Any,
    dry_run: bool = False,
    grace_seconds: int = 0,
    prefixes: list[str] | None = None,
) -> dict[str, Any]:
    """Purge orphaned leaf blobs and media assets from BOTH object storage (S3) and local disk storage.

    A blob is considered orphaned if its path is not referenced in the database by any
    Image (raw_path, processed_path), Prediction (raw_path, processed_path),
    or DatasetCandidate (image_path).

    Args:
        session: Active SQLAlchemy database session.
        dry_run: If True, returns count and list of unreferenced files without deleting them.
        grace_seconds: Minimum age of files in seconds before they can be considered orphaned.
                       (Protects in-flight prediction uploads from being deleted before DB commit).
        prefixes: Target storage prefixes/folders (default: ["uploads", "processed", "audio"]).

    Returns:
        Summary dict containing overall deleted count, local deleted count, and S3 deleted count.
    """
    prefixes = prefixes or ["uploads", "processed"]
    from app.models import Image, Prediction, DatasetCandidate

    valid_keys: set[str] = set()

    # 1. Images table
    try:
        for img in session.query(Image).all():
            for p in (img.raw_path, img.processed_path):
                if p:
                    clean = p.replace("\\", "/").strip("/")
                    valid_keys.add(clean)
                    if clean.startswith("data/"):
                        valid_keys.add(clean[5:])
                    else:
                        valid_keys.add(f"data/{clean}")
    except Exception as exc:
        logger.warning("Error scanning Image records: %s", exc)

    # 2. Predictions table
    try:
        for pred in session.query(Prediction).all():
            for p in (getattr(pred, "raw_path", None), getattr(pred, "processed_path", None)):
                if p:
                    clean = p.replace("\\", "/").strip("/")
                    valid_keys.add(clean)
                    if clean.startswith("data/"):
                        valid_keys.add(clean[5:])
                    else:
                        valid_keys.add(f"data/{clean}")
    except Exception as exc:
        logger.warning("Error scanning Prediction records: %s", exc)

    # 3. DatasetCandidate table
    try:
        for cand in session.query(DatasetCandidate).all():
            if cand.image_path:
                clean = cand.image_path.replace("\\", "/").strip("/")
                valid_keys.add(clean)
                if clean.startswith("data/"):
                    valid_keys.add(clean[5:])
                else:
                    valid_keys.add(f"data/{clean}")
    except Exception as exc:
        logger.warning("Error scanning DatasetCandidate records: %s", exc)

    now = time.time()
    now_utc = datetime.now(timezone.utc)

    # ── 1. Purge from Local Storage ──
    local_deleted = 0
    local_would_delete: list[str] = []

    for prefix in prefixes:
        prefix_dir = (settings.DATA_ROOT / prefix).resolve()
        if not prefix_dir.exists():
            continue
        for file_path in prefix_dir.rglob("*"):
            if not file_path.is_file():
                continue
            if grace_seconds > 0 and (now - file_path.stat().st_mtime < grace_seconds):
                continue

            try:
                rel_to_data = file_path.relative_to(settings.DATA_ROOT).as_posix()
            except ValueError:
                continue
            data_key = f"data/{rel_to_data}"

            if rel_to_data not in valid_keys and data_key not in valid_keys:
                if dry_run:
                    local_would_delete.append(data_key)
                else:
                    try:
                        file_path.unlink()
                        local_deleted += 1
                    except Exception as err:
                        logger.warning("Failed to delete local file %s: %s", file_path, err)

    # ── 2. Purge from Object Storage (S3) ──
    s3_deleted = 0
    s3_would_delete: list[str] = []
    s3_error: str | None = None

    if settings.AWS_S3_BUCKET:
        try:
            s3_backend = S3StorageBackend()
            client = s3_backend.client
            paginator = client.get_paginator("list_objects_v2")

            for prefix in prefixes:
                norm_prefix = prefix.strip("/") + "/"
                try:
                    for page in paginator.paginate(Bucket=s3_backend.bucket_name, Prefix=norm_prefix):
                        for item in page.get("Contents", []):
                            key = item.get("Key", "")
                            if not key or key.endswith("/"):
                                continue

                            if grace_seconds > 0:
                                last_mod = item.get("LastModified")
                                if last_mod and (now_utc - last_mod).total_seconds() < grace_seconds:
                                    continue

                            norm_key = key.replace("\\", "/").strip("/")
                            rel_key = norm_key[5:] if norm_key.startswith("data/") else norm_key
                            data_key = f"data/{rel_key}"

                            if norm_key not in valid_keys and rel_key not in valid_keys and data_key not in valid_keys:
                                if dry_run:
                                    s3_would_delete.append(key)
                                else:
                                    try:
                                        client.delete_object(Bucket=s3_backend.bucket_name, Key=key)
                                        s3_deleted += 1
                                    except Exception as err:
                                        logger.warning("Failed to delete S3 key %s: %s", key, err)
                except Exception as prefix_err:
                    logger.warning("Failed to list S3 prefix %s: %s", prefix, prefix_err)
        except Exception as exc:
            logger.warning("Object storage purge skipped or failed: %s", exc)
            s3_error = str(exc)

    if dry_run:
        return {
            "status": "dry_run",
            "unreferenced_files_count": len(local_would_delete) + len(s3_would_delete),
            "local_unreferenced_count": len(local_would_delete),
            "s3_unreferenced_count": len(s3_would_delete),
            "files": (local_would_delete + s3_would_delete)[:50],
            "local_files": local_would_delete[:25],
            "s3_files": s3_would_delete[:25],
            "s3_error": s3_error,
        }

    return {
        "status": "success",
        "deleted_files": local_deleted + s3_deleted,
        "local_deleted": local_deleted,
        "s3_deleted": s3_deleted,
        "s3_error": s3_error,
    }


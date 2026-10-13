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
        """Get an authorized download/view URL (signed URL for Supabase, static path for local)."""
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


class SupabaseStorageBackend(StorageBackend):
    """Supabase Object Storage implementation using Supabase REST API."""

    def __init__(
        self,
        supabase_url: str | None = None,
        service_role_key: str | None = None,
        bucket_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        raw_url = supabase_url or getattr(settings, "SUPABASE_URL", None) or ""
        self.supabase_url = raw_url.rstrip("/")
        self.service_role_key = (
            service_role_key
            or getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", None)
            or getattr(settings, "SUPABASE_KEY", None)
            or ""
        )
        self.bucket_name = (
            bucket_name
            or getattr(settings, "SUPABASE_BUCKET", None)
            or "smart-farming-data-dev"
        )

    def _normalize_key(self, key: str) -> str:
        clean = key.replace("\\", "/").strip("/")
        if clean.startswith("data/"):
            clean = clean[5:]
        return clean

    def _get_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.service_role_key:
            headers["Authorization"] = f"Bearer {self.service_role_key}"
            headers["apikey"] = self.service_role_key
        return headers

    def save(self, content: bytes, destination_key: str, content_type: str = "application/octet-stream") -> str:
        import httpx

        norm_key = self._normalize_key(destination_key)
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{norm_key}"
        headers = self._get_headers()
        headers["Content-Type"] = content_type
        headers["x-upsert"] = "true"

        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, headers=headers, content=content)
            if resp.status_code not in (200, 201):
                raise RuntimeError(f"Supabase storage upload failed ({resp.status_code}): {resp.text}")
        return norm_key

    def get(self, key: str) -> bytes:
        import httpx

        norm_key = self._normalize_key(key)
        url = f"{self.supabase_url}/storage/v1/object/authenticated/{self.bucket_name}/{norm_key}"
        headers = self._get_headers()

        with httpx.Client(timeout=30.0) as client:
            resp = client.get(url, headers=headers)
            if resp.status_code == 404:
                raise FileNotFoundError(f"Object not found in Supabase storage: {norm_key}")
            if resp.status_code != 200:
                raise RuntimeError(f"Supabase storage get failed ({resp.status_code}): {resp.text}")
            return resp.content

    def get_url(self, key: str, expires_in: int = 900) -> str:
        import httpx

        norm_key = self._normalize_key(key)
        url = f"{self.supabase_url}/storage/v1/object/sign/{self.bucket_name}/{norm_key}"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(url, headers=headers, json={"expiresIn": expires_in})
                if resp.status_code == 200:
                    data = resp.json()
                    signed = data.get("signedURL") or data.get("signedUrl") or ""
                    if signed.startswith("http"):
                        return signed
                    if signed.startswith("/"):
                        return f"{self.supabase_url}{signed}"
                    return f"{self.supabase_url}/{signed}"
                else:
                    logger.warning("Supabase signed URL error (%s): %s", resp.status_code, resp.text)
        except Exception as exc:
            logger.warning("Supabase signed URL generation failed for %s: %s", norm_key, exc)

        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{norm_key}"

    def delete(self, key: str) -> bool:
        import httpx

        norm_key = self._normalize_key(key)
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.request("DELETE", url, headers=headers, json={"prefixes": [norm_key]})
                return resp.status_code in (200, 204)
        except Exception as exc:
            logger.warning("Supabase delete failed for %s: %s", norm_key, exc)
            return False

    def exists(self, key: str) -> bool:
        import httpx

        norm_key = self._normalize_key(key)
        url = f"{self.supabase_url}/storage/v1/object/authenticated/{self.bucket_name}/{norm_key}"
        headers = self._get_headers()

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.head(url, headers=headers)
                if resp.status_code == 200:
                    return True
                if resp.status_code == 405:
                    resp = client.get(url, headers={**headers, "Range": "bytes=0-0"})
                    return resp.status_code in (200, 206)
                return False
        except Exception:
            return False

    def list_objects(self, prefix: str = "") -> list[str]:
        import httpx

        norm_prefix = self._normalize_key(prefix) if prefix else ""
        url = f"{self.supabase_url}/storage/v1/object/list/{self.bucket_name}"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"

        keys: list[str] = []
        offset = 0
        limit = 100

        try:
            with httpx.Client(timeout=30.0) as client:
                while True:
                    payload = {
                        "prefix": norm_prefix,
                        "limit": limit,
                        "offset": offset,
                        "sortBy": {"column": "name", "order": "asc"},
                    }
                    resp = client.post(url, headers=headers, json=payload)
                    if resp.status_code != 200:
                        raise RuntimeError(f"Supabase list objects failed ({resp.status_code}): {resp.text}")
                    items = resp.json()
                    if not items:
                        break
                    for item in items:
                        name = item.get("name")
                        if name:
                            full_key = f"{norm_prefix}/{name}".strip("/") if norm_prefix else name
                            if item.get("id") is not None:
                                keys.append(full_key)
                            else:
                                # Subdirectory / folder, recurse to fetch nested keys
                                sub_keys = self.list_objects(prefix=full_key)
                                keys.extend(sub_keys)
                    if len(items) < limit:
                        break
                    offset += limit
        except Exception as exc:
            logger.warning("Supabase list objects exception: %s", exc)
            raise

        return keys


# Backward compatibility alias
S3StorageBackend = SupabaseStorageBackend

_STORAGE_INSTANCE: StorageBackend | None = None


def get_storage() -> StorageBackend:
    """Singleton accessor for configured storage backend."""
    global _STORAGE_INSTANCE
    if _STORAGE_INSTANCE is None:
        backend_type = (settings.STORAGE_BACKEND or "local").lower()
        if backend_type in ("supabase", "s3"):
            logger.info("Initializing SupabaseStorageBackend for bucket: %s (%s)", settings.SUPABASE_BUCKET, settings.SUPABASE_URL)
            _STORAGE_INSTANCE = SupabaseStorageBackend()
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
    """Purge orphaned leaf blobs and media assets from BOTH object storage (Supabase) and local disk storage.

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
        Summary dict containing overall deleted count, local deleted count, and Supabase deleted count.
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

    # ── 2. Purge from Supabase Storage ──
    cloud_deleted = 0
    cloud_would_delete: list[str] = []
    cloud_error: str | None = None

    target_bucket = getattr(settings, "SUPABASE_BUCKET", None) or getattr(settings, "AWS_S3_BUCKET", None)
    if target_bucket and (settings.STORAGE_BACKEND or "local").lower() in ("supabase", "s3"):
        try:
            cloud_backend = SupabaseStorageBackend()
            for prefix in prefixes:
                try:
                    objects = cloud_backend.list_objects(prefix=prefix)
                    for key in objects:
                        if not key or key.endswith("/"):
                            continue

                        norm_key = key.replace("\\", "/").strip("/")
                        rel_key = norm_key[5:] if norm_key.startswith("data/") else norm_key
                        data_key = f"data/{rel_key}"

                        if norm_key not in valid_keys and rel_key not in valid_keys and data_key not in valid_keys:
                            if dry_run:
                                cloud_would_delete.append(key)
                            else:
                                if cloud_backend.delete(key):
                                    cloud_deleted += 1
                except Exception as prefix_err:
                    logger.warning("Failed to list Supabase storage prefix %s: %s", prefix, prefix_err)
        except Exception as exc:
            logger.warning("Supabase storage purge skipped or failed: %s", exc)
            cloud_error = str(exc)

    if dry_run:
        return {
            "status": "dry_run",
            "unreferenced_files_count": len(local_would_delete) + len(cloud_would_delete),
            "local_unreferenced_count": len(local_would_delete),
            "cloud_unreferenced_count": len(cloud_would_delete),
            "supabase_unreferenced_count": len(cloud_would_delete),
            "s3_unreferenced_count": len(cloud_would_delete),
            "files": (local_would_delete + cloud_would_delete)[:50],
            "local_files": local_would_delete[:25],
            "cloud_files": cloud_would_delete[:25],
            "cloud_error": cloud_error,
        }

    return {
        "status": "success",
        "deleted_files": local_deleted + cloud_deleted,
        "local_deleted": local_deleted,
        "cloud_deleted": cloud_deleted,
        "supabase_deleted": cloud_deleted,
        "s3_deleted": cloud_deleted,
        "cloud_error": cloud_error,
    }


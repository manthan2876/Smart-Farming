from __future__ import annotations

import io
import re
import time
import urllib.parse
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
        segments = [s for s in clean.split("/") if s and s != "."]
        if any(s == ".." for s in segments):
            raise ValueError(f"Directory traversal detected in storage key: {key}")
        for s in segments:
            if not s.replace("-", "").replace("_", "").replace(".", "").isalnum():
                raise ValueError(f"Invalid character in storage key segment: {s}")
        return "/".join(urllib.parse.quote(s, safe=".-_~") for s in segments)

    def _get_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.service_role_key:
            headers["Authorization"] = f"Bearer {self.service_role_key}"
            headers["apikey"] = self.service_role_key
        return headers

    def save(self, content: bytes, destination_key: str, content_type: str = "application/octet-stream") -> str:
        import httpx

        norm_key = self._normalize_key(destination_key)
        safe_bucket = urllib.parse.quote(str(self.bucket_name), safe=".-_~")
        safe_key = "/".join(urllib.parse.quote(seg, safe=".-_~") for seg in norm_key.split("/"))
        url = f"{self.supabase_url}/storage/v1/object/{safe_bucket}/{safe_key}"
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
        safe_bucket = urllib.parse.quote(str(self.bucket_name), safe=".-_~")
        key_segments = norm_key.split("/")
        safe_segments = []
        for seg in key_segments:
            tokens = [tok for tok in re.split(r"[-_.]", seg) if tok]
            if not all(tok.isalnum() for tok in tokens):
                raise ValueError(f"Invalid characters in storage key segment: {seg}")
            safe_segments.append(seg)
        safe_key = "/".join(urllib.parse.quote(s, safe=".-_~") for s in safe_segments)
        url = f"{self.supabase_url}/storage/v1/object/authenticated/{safe_bucket}/{safe_key}"
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
        safe_bucket = urllib.parse.quote(str(self.bucket_name), safe=".-_~")
        safe_key = "/".join(urllib.parse.quote(seg, safe=".-_~") for seg in norm_key.split("/"))
        url = f"{self.supabase_url}/storage/v1/object/sign/{safe_bucket}/{safe_key}"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(url, headers=headers, json={"expiresIn": expires_in})
                if resp.status_code == 200:
                    data = resp.json()
                    signed = data.get("signedURL") or data.get("signedUrl") or ""
                    if signed.startswith("http"):
                        if ".supabase.co/object/sign/" in signed:
                            signed = signed.replace(".supabase.co/object/sign/", ".supabase.co/storage/v1/object/sign/")
                        return signed
                    if not signed.startswith("/"):
                        signed = f"/{signed}"
                    if not signed.startswith("/storage/v1"):
                        signed = f"/storage/v1{signed}"
                    return f"{self.supabase_url}{signed}"
                else:
                    logger.warning("Supabase signed URL error (%s): %s", resp.status_code, resp.text)
        except Exception as exc:
            logger.warning("Supabase signed URL generation failed for %s: %s", norm_key, exc)

        return f"/data/{norm_key}"

    def delete(self, key: str) -> bool:
        import httpx

        norm_key = self._normalize_key(key)
        safe_bucket = urllib.parse.quote(str(self.bucket_name), safe=".-_~")
        url = f"{self.supabase_url}/storage/v1/object/{safe_bucket}"
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
        safe_bucket = urllib.parse.quote(str(self.bucket_name), safe=".-_~")
        safe_key = "/".join(urllib.parse.quote(seg, safe=".-_~") for seg in norm_key.split("/"))
        url = f"{self.supabase_url}/storage/v1/object/authenticated/{safe_bucket}/{safe_key}"
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
            cloud_error = "Storage backend purge encountered an internal error."

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


def compress_image_bytes(
    image_bytes: bytes,
    max_dim: int = 1280,
    quality: int = 85,
) -> tuple[bytes, str]:
    """Downscale and compress image bytes if dimensions exceed max_dim or to optimize storage size.

    - Preserves aspect ratio when downscaling.
    - Applies EXIF orientation tags before processing.
    - Converts RGBA/transparency to RGB on a white background.
    - Saves as optimized JPEG (quality=85).
    - Returns (compressed_bytes, "image/jpeg") if successfully processed and smaller or resized,
      otherwise returns the original bytes and content type.
    """
    try:
        from PIL import Image as PILImage, ImageOps

        with PILImage.open(io.BytesIO(image_bytes)) as img:
            img = ImageOps.exif_transpose(img)
            width, height = img.size
            needs_resize = width > max_dim or height > max_dim
            if needs_resize:
                img.thumbnail((max_dim, max_dim), PILImage.Resampling.LANCZOS)

            if img.mode in ("RGBA", "LA", "P"):
                background = PILImage.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                alpha = img.split()[-1] if img.mode == "RGBA" else None
                background.paste(img, mask=alpha)
                out_img = background
            elif img.mode != "RGB":
                out_img = img.convert("RGB")
            else:
                out_img = img

            buffer = io.BytesIO()
            out_img.save(buffer, format="JPEG", quality=quality, optimize=True)
            compressed = buffer.getvalue()
            if len(compressed) < len(image_bytes) or needs_resize:
                return compressed, "image/jpeg"
    except Exception as exc:
        logger.warning("Image compression skipped or failed: %s", exc)
    return image_bytes, "image/jpeg"


def prune_cached_audio(
    dry_run: bool = False,
    max_age_days: int = 30,
) -> dict[str, Any]:
    """Prune cached TTS audio files (.mp3, .wav) older than max_age_days from local disk and Supabase storage."""
    cutoff_seconds = max_age_days * 86400
    now = time.time()
    local_deleted = 0
    cloud_deleted = 0
    cloud_error = None

    # 1. Local pruning
    unique_dirs = {p.resolve() for p in (settings.AUDIO_ROOT, settings.DATA_ROOT / "audio") if p}
    for resolved in unique_dirs:
        try:
            if not resolved.exists():
                continue
            for file_path in resolved.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in (".mp3", ".wav"):
                    try:
                        if (now - file_path.stat().st_mtime) > cutoff_seconds:
                            if not dry_run:
                                file_path.unlink()
                            local_deleted += 1
                    except Exception as exc:
                        logger.warning("Failed to delete expired audio %s: %s", file_path, exc)
        except Exception:
            # Local audio directory access or scanning failed; proceed to cloud pruning
            pass

    # 2. Supabase storage pruning
    target_bucket = getattr(settings, "SUPABASE_BUCKET", None) or getattr(settings, "AWS_S3_BUCKET", None)
    if target_bucket and (settings.STORAGE_BACKEND or "local").lower() in ("supabase", "s3"):
        try:
            cloud_backend = SupabaseStorageBackend()
            import httpx

            url = f"{cloud_backend.supabase_url}/storage/v1/object/list/{cloud_backend.bucket_name}"
            headers = cloud_backend._get_headers()
            headers["Content-Type"] = "application/json"
            offset = 0
            limit = 100
            expired_keys: list[str] = []

            with httpx.Client(timeout=30.0) as client:
                while True:
                    payload = {"prefix": "audio", "limit": limit, "offset": offset}
                    resp = client.post(url, headers=headers, json=payload)
                    if resp.status_code != 200:
                        break
                    items = resp.json()
                    if not items:
                        break
                    for item in items:
                        name = item.get("name")
                        if not name:
                            continue
                        created_str = item.get("created_at") or item.get("updated_at")
                        if created_str:
                            try:
                                dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                                age = (datetime.now(timezone.utc) - dt).total_seconds()
                                if age > cutoff_seconds:
                                    expired_keys.append(f"audio/{name}")
                            except Exception:
                                # Malformed timestamp string in object metadata; skip item age calculation
                                pass
                    if len(items) < limit:
                        break
                    offset += limit

            for key in expired_keys:
                if dry_run:
                    cloud_deleted += 1
                else:
                    if cloud_backend.delete(key):
                        cloud_deleted += 1
        except Exception as exc:
            logger.warning("Supabase audio pruning failed: %s", exc)
            cloud_error = "An error occurred while pruning cloud audio."

    return {
        "status": "dry_run" if dry_run else "success",
        "local_pruned": local_deleted,
        "cloud_pruned": cloud_deleted,
        "total_pruned": local_deleted + cloud_deleted,
        "cloud_error": cloud_error,
    }


def prune_unflagged_heatmaps(
    session: Any,
    dry_run: bool = False,
    max_age_days: int = 7,
) -> dict[str, Any]:
    """Prune processed heatmaps for scans older than max_age_days that have no expert reviews,
    dataset candidate inclusion, or negative feedback. Missing heatmaps will self-heal on demand if viewed."""
    from datetime import timedelta
    from app.models import Prediction, DatasetCandidate

    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    pruned_count = 0
    storage = get_storage()

    try:
        candidates = (
            session.query(Prediction)
            .filter(
                Prediction.created_at < cutoff,
                Prediction.processed_path.isnot(None),
            )
            .all()
        )

        for pred in candidates:
            # Skip if pending review or flagged
            if pred.status in ("pending_expert_review", "flagged"):
                continue
            # Skip if has expert review
            if pred.expert_review is not None:
                continue
            # Skip if user reported incorrect feedback
            if any(fb.rating and fb.rating <= 2 for fb in (pred.feedback or [])):
                continue
            if any(fb.feedback_type == "incorrect" for fb in (pred.feedback or [])):
                continue
            # Skip if marked as retraining candidate
            cand = session.query(DatasetCandidate).filter(DatasetCandidate.prediction_id == pred.id).first()
            if cand is not None:
                continue

            old_proc = pred.processed_path
            if not old_proc:
                continue

            norm_key = old_proc.replace("\\", "/").strip("/")
            rel_key = norm_key[5:] if norm_key.startswith("data/") else norm_key

            if not dry_run:
                # 1. Remove local file
                local_file = settings.DATA_ROOT / rel_key
                if local_file.is_file():
                    try:
                        local_file.unlink()
                    except Exception as err:
                        logger.warning("Could not delete local heatmap %s: %s", local_file, err)

                # 2. Remove cloud file
                try:
                    storage.delete(rel_key)
                except Exception as err:
                    logger.warning("Could not delete cloud heatmap %s: %s", rel_key, err)

                # 3. Update DB
                pred.processed_path = None
                if isinstance(pred.result, dict):
                    res = dict(pred.result)
                    if "image" in res and isinstance(res["image"], dict):
                        res["image"]["processed_path"] = None
                    pred.result = res
                if pred.image:
                    pred.image.processed_path = None

            pruned_count += 1

        if not dry_run and pruned_count > 0:
            session.commit()

    except Exception as exc:
        logger.error("Error during heatmap pruning: %s", exc)
        return {"status": "error", "error": "An error occurred during heatmap pruning.", "heatmaps_pruned": pruned_count}

    return {
        "status": "dry_run" if dry_run else "success",
        "heatmaps_pruned": pruned_count,
        "max_age_days": max_age_days,
    }


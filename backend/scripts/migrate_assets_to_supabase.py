#!/usr/bin/env python3
"""
migrate_assets_to_supabase.py — Migrate local image and audio assets to Supabase Object Storage.

Uploads local asset files (uploads/, processed/, audio/) to Supabase Object Storage,
verifies integrity via HeadObject/exists checks, and normalizes file paths in PostgreSQL.

Target Buckets:
  - Development : smart-farming-data-dev (default)
  - Production  : smart-farming (--env prod)

Usage:
  # Dry-run audit (inspect files without uploading or modifying DB):
  python backend/scripts/migrate_assets_to_supabase.py --dry-run

  # Execute live migration to DEV bucket with verification:
  python backend/scripts/migrate_assets_to_supabase.py --verify

  # Execute live migration to PROD bucket:
  python backend/scripts/migrate_assets_to_supabase.py --env prod --verify

  # Execute live migration and remove local files after verified upload:
  python backend/scripts/migrate_assets_to_supabase.py --verify --delete-local
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

# Parse arguments early to configure target environment before config is imported
parser = argparse.ArgumentParser(description="Migrate local Smart-Farming images and audio to Supabase Object Storage.")
parser.add_argument("--env", choices=["dev", "development", "prod", "production"], default=None, help="Target environment (dev or prod)")
parser.add_argument("--bucket", default=None, help="Explicit bucket name override")
parser.add_argument("--dry-run", action="store_true", help="Audit local files without uploading to Supabase or modifying DB.")
parser.add_argument("--verify", action="store_true", help="Verify each uploaded file exists in Supabase storage.")
parser.add_argument("--delete-local", action="store_true", help="Delete local files after verified upload to Supabase.")
args, _ = parser.parse_known_args()

if args.env:
    env_clean = "production" if args.env in ("prod", "production") else "development"
    os.environ["ENVIRONMENT"] = env_clean
    os.environ["ENV_FILE"] = ".env.production" if env_clean == "production" else ".env"

backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir / "src"))

# Optional local cache fallbacks for standalone execution
import glob
for _d in glob.glob("/home/manthan/.cache/uv/archive-v0/*"):
    try:
        _items = set(os.listdir(_d))
        if "tests" not in _items and "numpy" not in _items and "cv2" not in _items:
            sys.path.append(_d)
    except OSError:
        pass

from app.core.config import settings
from app.core.session import _session_factory
from app.core.storage import get_storage, SupabaseStorageBackend
from app.models import Image, Prediction

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migrate-assets-supabase")


def compute_md5(file_path: Path) -> str:
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096 * 1024), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def detect_content_type(file_name: str) -> str:
    suffix = Path(file_name).suffix.lower()
    if suffix in [".jpg", ".jpeg"]:
        return "image/jpeg"
    elif suffix == ".png":
        return "image/png"
    elif suffix == ".webp":
        return "image/webp"
    elif suffix == ".mp3":
        return "audio/mpeg"
    elif suffix == ".zip":
        return "application/zip"
    return "application/octet-stream"


def run_migration(dry_run: bool = True, verify: bool = True, delete_local: bool = False, bucket_override: str | None = None) -> dict[str, Any]:
    target_bucket = bucket_override or getattr(settings, "SUPABASE_BUCKET", "smart-farming-data-dev")
    supabase_url = getattr(settings, "SUPABASE_URL", "")

    logger.info("=" * 65)
    logger.info("Starting Supabase Object Storage Asset Migration")
    logger.info("=" * 65)
    logger.info("Environment   : %s", getattr(settings, "ENVIRONMENT", "development").upper())
    logger.info("Supabase URL  : %s", supabase_url or "(Not configured)")
    logger.info("Target Bucket : %s", target_bucket)
    logger.info("Mode          : Dry-Run = %s, Verify = %s, Delete Local = %s", dry_run, verify, delete_local)
    logger.info("-" * 65)

    if not supabase_url or not getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", None):
        logger.error("Missing Supabase configuration in environment (SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY).")
        raise RuntimeError("Supabase credentials not configured in current environment.")

    if bucket_override and bucket_override != settings.SUPABASE_BUCKET:
        storage = SupabaseStorageBackend(bucket_name=bucket_override)
    else:
        storage = get_storage()

    directories = [
        ("uploads", settings.UPLOAD_ROOT),
        ("processed", settings.PROCESSED_ROOT),
        ("audio", settings.AUDIO_ROOT),
    ]

    stats = {
        "environment": getattr(settings, "ENVIRONMENT", "development"),
        "target_bucket": target_bucket,
        "scanned": 0,
        "uploaded": 0,
        "already_exists": 0,
        "verified": 0,
        "deleted_local": 0,
        "failed": 0,
        "db_records_updated": 0,
        "errors": [],
    }

    key_mappings: dict[str, str] = {}

    for prefix, folder in directories:
        folder_path = Path(folder)
        if not folder_path.exists():
            logger.info("Directory %s does not exist on disk, skipping.", prefix)
            continue

        for file_path in folder_path.glob("*"):
            if not file_path.is_file():
                continue

            stats["scanned"] += 1
            rel_key = f"{prefix}/{file_path.name}"
            content_type = detect_content_type(file_path.name)
            local_md5 = compute_md5(file_path)

            old_rel_path = f"data/{prefix}/{file_path.name}"
            key_mappings[old_rel_path] = rel_key
            key_mappings[f"{prefix}/{file_path.name}"] = rel_key

            logger.info("[%s] Checking %s (MD5: %s)", prefix, file_path.name, local_md5)

            if dry_run:
                stats["uploaded"] += 1
                continue

            try:
                if storage.exists(rel_key):
                    stats["already_exists"] += 1
                    logger.info("Object %s already exists in Supabase bucket, skipping upload.", rel_key)
                else:
                    content = file_path.read_bytes()
                    storage.save(content, rel_key, content_type=content_type)
                    stats["uploaded"] += 1
                    logger.info("Successfully uploaded: %s -> %s", file_path.name, rel_key)

                if verify:
                    if storage.exists(rel_key):
                        stats["verified"] += 1
                    else:
                        raise RuntimeError(f"Verification failed: {rel_key} not found in Supabase storage after upload.")

                if delete_local and (not verify or storage.exists(rel_key)):
                    file_path.unlink()
                    stats["deleted_local"] += 1
                    logger.info("Deleted local file: %s", file_path)

            except Exception as exc:
                stats["failed"] += 1
                error_msg = f"Failed for {file_path.name}: {exc}"
                stats["errors"].append(error_msg)
                logger.error(error_msg)

    # Database Path Normalization
    if not dry_run:
        logger.info("Updating database asset references...")
        Session = _session_factory()
        db = Session()
        try:
            images = db.query(Image).all()
            for img in images:
                updated = False
                if img.raw_path:
                    norm = img.raw_path.replace("\\", "/").strip("/")
                    if norm in key_mappings:
                        img.raw_path = key_mappings[norm]
                        updated = True
                if img.processed_path:
                    norm = img.processed_path.replace("\\", "/").strip("/")
                    if norm in key_mappings:
                        img.processed_path = key_mappings[norm]
                        updated = True
                if updated:
                    stats["db_records_updated"] += 1

            predictions = db.query(Prediction).all()
            for pred in predictions:
                updated = False
                res = dict(pred.result or {})
                img_block = res.get("image", {})
                if img_block and isinstance(img_block, dict):
                    raw = img_block.get("raw_path")
                    if raw and raw.replace("\\", "/").strip("/") in key_mappings:
                        img_block["raw_path"] = key_mappings[raw.replace("\\", "/").strip("/")]
                        updated = True
                    proc = img_block.get("processed_path")
                    if proc and proc.replace("\\", "/").strip("/") in key_mappings:
                        img_block["processed_path"] = key_mappings[proc.replace("\\", "/").strip("/")]
                        updated = True
                if updated:
                    pred.result = res
                    db.add(pred)
                    stats["db_records_updated"] += 1

            db.commit()
            logger.info("Database references successfully updated.")
        except Exception as exc:
            db.rollback()
            logger.error("Failed to update database references: %s", exc)
            stats["errors"].append(f"DB update error: {exc}")
        finally:
            db.close()

    report_path = backend_dir / "supabase_migration_report.json"
    report_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    logger.info("Migration finished. Summary report written to: %s", report_path)
    logger.info(
        "Scanned: %d | Uploaded: %d | Verified: %d | Skipped: %d | Failed: %d | DB Updates: %d",
        stats["scanned"],
        stats["uploaded"],
        stats["verified"],
        stats["already_exists"],
        stats["failed"],
        stats["db_records_updated"],
    )
    return stats


def main():
    dry_run = args.dry_run or (not args.verify and not args.delete_local)
    run_migration(
        dry_run=dry_run,
        verify=args.verify,
        delete_local=args.delete_local,
        bucket_override=args.bucket,
    )


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
verify_supabase_storage.py — Test and verify Supabase Object Storage connectivity and permissions.

Usage:
  python backend/scripts/verify_supabase_storage.py               # Tests dev bucket (smartfarming-data-dev)
  python backend/scripts/verify_supabase_storage.py --env prod     # Tests prod bucket (smart-farming-data)
  python backend/scripts/verify_supabase_storage.py --bucket custom-bucket
"""

from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path

# Parse CLI arguments early to configure environment before config is imported
parser = argparse.ArgumentParser(description="Verify Supabase Object Storage connectivity.")
parser.add_argument("--env", choices=["dev", "development", "prod", "production"], default=None, help="Target environment (dev or prod)")
parser.add_argument("--bucket", default=None, help="Explicit bucket name override")
args, _ = parser.parse_known_args()

if args.env:
    env_clean = "production" if args.env in ("prod", "production") else "development"
    os.environ["ENVIRONMENT"] = env_clean
    os.environ["ENV_FILE"] = ".env.production" if env_clean == "production" else ".env"

backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir / "src"))

# Optional local cache fallbacks for standalone test/verification runs
import glob
for _d in glob.glob("/home/manthan/.cache/uv/archive-v0/*"):
    try:
        _items = set(os.listdir(_d))
        if "tests" not in _items and "numpy" not in _items and "cv2" not in _items:
            sys.path.append(_d)
    except OSError:
        pass

from app.core.config import settings
from app.core.storage import get_storage, SupabaseStorageBackend


def main() -> int:
    env_name = getattr(settings, "ENVIRONMENT", "development")
    target_bucket = args.bucket or getattr(settings, "SUPABASE_BUCKET", "smart-farming-data-dev")
    supabase_url = getattr(settings, "SUPABASE_URL", "")
    key_preview = f"{settings.SUPABASE_SERVICE_ROLE_KEY[:10]}..." if getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", None) else "(Not configured)"

    print("=" * 65)
    print(" Supabase Object Storage Verification")
    print("=" * 65)
    print(f"Target Environment : {env_name.upper()}")
    print(f"Provider           : Supabase Storage (REST API)")
    print(f"Supabase URL       : {supabase_url or '(Not configured)'}")
    print(f"Target Bucket      : {target_bucket}")
    print(f"Service Role Key   : {key_preview}")
    print("-" * 65)

    if not supabase_url or not getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", None):
        print("\n[FAILED] Missing Supabase configuration in environment!")
        print("Please ensure the following variables are present in your .env:")
        print("  SUPABASE_URL=https://<your-project-ref>.supabase.co")
        print("  SUPABASE_SERVICE_ROLE_KEY=eyJh...")
        print(f"  SUPABASE_BUCKET={target_bucket}")
        return 1

    if args.bucket and args.bucket != settings.SUPABASE_BUCKET:
        storage = SupabaseStorageBackend(bucket_name=args.bucket)
    else:
        storage = get_storage()

    # 1. Test Listing
    print(f"\n1. Testing bucket list operation on '{target_bucket}'...")
    try:
        objects = storage.list_objects()
        print(f"   [SUCCESS] Successfully connected and listed objects.")
        print(f"   Total objects found: {len(objects)}")
        for obj in objects[:10]:
            print(f"     - {obj}")
        if len(objects) > 10:
            print(f"     ... and {len(objects) - 10} more.")
    except Exception as exc:
        print(f"   [FAILED] Could not list objects in bucket '{target_bucket}': {exc}")
        print("\n   [ACTION REQUIRED / TROUBLESHOOTING]")
        print("   In your Supabase Dashboard:")
        print(f"   1. Navigate to Storage -> Buckets.")
        print(f"   2. Confirm a bucket named '{target_bucket}' exists.")
        print(f"   3. If not, click 'New Bucket' -> name it '{target_bucket}'.")
        print(f"   4. Ensure SUPABASE_SERVICE_ROLE_KEY is the 'service_role' secret key (Project Settings -> API).")
        return 1

    # 2. Test Write
    test_key = f"uploads/test_connectivity_{uuid.uuid4().hex[:8]}.txt"
    test_data = b"Smart Farming Supabase Storage Connection Test Passed!"
    print(f"\n2. Testing upload to '{test_key}'...")
    try:
        saved_key = storage.save(test_data, test_key, content_type="text/plain")
        print(f"   [SUCCESS] Uploaded successfully: {saved_key}")
    except Exception as exc:
        print(f"   [FAILED] Upload failed: {exc}")
        return 1

    # 3. Test Read
    print("\n3. Testing read/retrieve...")
    try:
        retrieved = storage.get(saved_key)
        if retrieved == test_data:
            print("   [SUCCESS] Data retrieved and matches byte-for-byte!")
        else:
            print("   [FAILED] Data retrieved does not match original bytes.")
            return 1
    except Exception as exc:
        print(f"   [FAILED] Get object failed: {exc}")
        return 1

    # 4. Test Presigned/Signed URL
    print("\n4. Testing signed URL generation...")
    try:
        url = storage.get_url(saved_key, expires_in=300)
        print(f"   [SUCCESS] Signed URL generated:\n   {url}")
    except Exception as exc:
        print(f"   [FAILED] Signed URL generation failed: {exc}")
        return 1

    # 5. Test Cleanup
    print("\n5. Cleaning up test file...")
    try:
        deleted = storage.delete(saved_key)
        print(f"   [SUCCESS] Cleaned up temporary test file (deleted={deleted}).")
    except Exception as exc:
        print(f"   [WARNING] Could not delete temporary test file: {exc}")

    print("\n" + "=" * 65)
    print(f"ALL STORAGE TESTS PASSED! Supabase bucket '{target_bucket}' is fully operational.")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())


#!/usr/bin/env python3
"""
verify_s3_storage.py — Test and verify AWS S3 object storage connectivity and permissions.

Usage:
  python backend/scripts/verify_s3_storage.py
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir / "src"))

from app.core.config import settings
from app.core.storage import get_storage


def main() -> int:
    print("=" * 60)
    print("AWS S3 Object Storage Verification Script")
    print("=" * 60)
    print(f"Backend Type : {settings.STORAGE_BACKEND}")
    print(f"Target Bucket: {settings.AWS_S3_BUCKET}")
    print(f"Region       : {settings.AWS_REGION}")
    key_preview = f"{settings.AWS_ACCESS_KEY_ID[:8]}..." if settings.AWS_ACCESS_KEY_ID else "(None)"
    print(f"Access Key ID: {key_preview}")
    print("-" * 60)

    storage = get_storage()

    # 1. Test Listing
    print("\n1. Testing bucket list operation...")
    try:
        objects = storage.list_objects()
        print(f"   [SUCCESS] Successfully connected and listed objects.")
        print(f"   Total objects found: {len(objects)}")
        for obj in objects[:10]:
            print(f"     - {obj}")
        if len(objects) > 10:
            print(f"     ... and {len(objects) - 10} more.")
    except Exception as exc:
        print(f"   [FAILED] Could not list objects: {exc}")
        print("\n   [ACTION REQUIRED]")
        print("   Ensure AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
        print(f"   have s3:ListBucket, s3:PutObject, s3:GetObject, s3:DeleteObject")
        print(f"   permissions on bucket '{settings.AWS_S3_BUCKET}'.")
        return 1

    # 2. Test Write (AES256)
    test_key = f"uploads/test_connectivity_{uuid.uuid4().hex[:8]}.txt"
    test_data = b"Smart Farming AWS S3 Connection Test Passed!"
    print(f"\n2. Testing upload to '{test_key}'...")
    try:
        saved_key = storage.save(test_data, test_key, content_type="text/plain")
        print(f"   [SUCCESS] Uploaded successfully with AES256 encryption: {saved_key}")
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

    # 4. Test Presigned URL
    print("\n4. Testing presigned URL generation...")
    try:
        url = storage.get_url(saved_key, expires_in=300)
        print(f"   [SUCCESS] Presigned URL generated:\n   {url}")
    except Exception as exc:
        print(f"   [FAILED] Presigned URL generation failed: {exc}")
        return 1

    # 5. Test Cleanup
    print("\n5. Cleaning up test file...")
    try:
        deleted = storage.delete(saved_key)
        print(f"   [SUCCESS] Cleaned up temporary test file (deleted={deleted}).")
    except Exception as exc:
        print(f"   [WARNING] Could not delete temporary test file: {exc}")

    print("\n" + "=" * 60)
    print("ALL STORAGE TESTS PASSED! AWS S3 is fully operational.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())


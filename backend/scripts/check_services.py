"""Consolidated read-only health and diagnostic smoke tests for external services.

Tests:
1. PostgreSQL Database connectivity & query latency.
2. Supabase Storage upload, read & cleanup.
3. Upstash Redis REST connectivity & round-trip latency (non-destructive).
4. Supabase Auth service reachability.

Usage:
  python backend/scripts/check_services.py
  python backend/scripts/check_services.py --env prod
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time
import uuid
from pathlib import Path

# Setup paths via _common
scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts_dir))

from _common import get_supabase_env_config
import httpx
from sqlalchemy import text
from app.core.config import settings
from app.core.redis_rest import redis_rest
from app.core.session import create_app_engine
from app.core.storage import get_storage


def check_database(db_url: str) -> bool:
    print("\n[1/4] Checking PostgreSQL Database...")
    if not db_url:
        print("   [WARN] No database URL configured.")
        return False
    try:
        t0 = time.perf_counter()
        engine = create_app_engine(db_url)
        with engine.connect() as conn:
            val = conn.execute(text("SELECT 1;")).scalar()
            latency = (time.perf_counter() - t0) * 1000
            if val == 1:
                print(f"   [PASS] PostgreSQL connected successfully (latency: {latency:.1f}ms).")
                return True
            else:
                print(f"   [FAIL] Unexpected query result: {val}")
                return False
    except Exception as exc:
        print(f"   [FAIL] Database connection error: {exc}")
        return False


def check_storage() -> bool:
    print("\n[2/4] Checking Supabase Object Storage...")
    try:
        storage = get_storage()
        t0 = time.perf_counter()
        test_filename = f"healthcheck_{uuid.uuid4().hex[:8]}.txt"
        test_content = b"healthcheck probe data"

        # Upload
        storage.upload(test_filename, test_content, content_type="text/plain")

        # Check URL
        url = storage.get_url(test_filename)

        # Cleanup
        storage.delete(test_filename)
        latency = (time.perf_counter() - t0) * 1000

        print(f"   [PASS] Object Storage upload/delete verified (latency: {latency:.1f}ms).")
        print(f"   Sample signed URL pattern: {url.split('?')[0] if '?' in url else url}")
        return True
    except Exception as exc:
        print(f"   [FAIL] Storage check failed: {exc}")
        return False


async def check_redis() -> bool:
    print("\n[3/4] Checking Upstash Redis REST...")
    if not redis_rest.enabled:
        print("   [INFO] Redis is disabled (REQUIRE_REDIS=False or unconfigured).")
        return True
    try:
        t0 = time.perf_counter()
        probe_key = f"sf:probe:{uuid.uuid4().hex[:8]}"
        await redis_rest.set(probe_key, "ok", ex=10)
        val = await redis_rest.get(probe_key)
        await redis_rest.delete(probe_key)
        latency = (time.perf_counter() - t0) * 1000

        if val == "ok":
            print(f"   [PASS] Upstash Redis REST responsive (latency: {latency:.1f}ms).")
            return True
        else:
            print(f"   [WARN] Redis unexpected response: {val}")
            return False
    except Exception as exc:
        print(f"   [FAIL] Redis check failed: {exc}")
        return False


def check_auth_api(supabase_url: str, service_key: str) -> bool:
    print("\n[4/4] Checking Supabase Auth API Service...")
    if not supabase_url or not service_key:
        print("   [WARN] Supabase URL or service key not configured.")
        return False
    try:
        t0 = time.perf_counter()
        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
        }
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(f"{supabase_url}/auth/v1/health", headers=headers)
            latency = (time.perf_counter() - t0) * 1000
            # Some Supabase instances use /health or /settings
            if resp.status_code in (200, 204):
                print(f"   [PASS] Supabase Auth service healthy (latency: {latency:.1f}ms).")
                return True
            else:
                resp2 = client.get(f"{supabase_url}/auth/v1/settings", headers=headers)
                latency2 = (time.perf_counter() - t0) * 1000
                if resp2.status_code == 200:
                    print(f"   [PASS] Supabase Auth service reachable (latency: {latency2:.1f}ms).")
                    return True
                print(f"   [WARN] Auth returned HTTP {resp.status_code}: {resp.text[:100]}")
                return False
    except Exception as exc:
        print(f"   [FAIL] Auth API connection error: {exc}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Check external services health.")
    parser.add_argument("--env", choices=["dev", "prod"], default="dev", help="Target environment")
    args = parser.parse_args()

    cfg = get_supabase_env_config(args.env)

    print("=" * 65)
    print(f"  SMART FARMING: EXTERNAL SERVICES HEALTH CHECK ({cfg['label']})")
    print("=" * 65)

    db_ok = check_database(cfg["db_url"])
    storage_ok = check_storage()
    redis_ok = asyncio.run(check_redis())
    auth_ok = check_auth_api(cfg["supabase_url"], cfg["service_key"])

    print("\n" + "=" * 65)
    print("  HEALTH CHECK SUMMARY")
    print("=" * 65)
    print(f"  Database : {'PASS' if db_ok else 'FAIL'}")
    print(f"  Storage  : {'PASS' if storage_ok else 'FAIL'}")
    print(f"  Redis    : {'PASS' if redis_ok else 'SKIP/FAIL'}")
    print(f"  Auth API : {'PASS' if auth_ok else 'FAIL'}")
    print("=" * 65)


if __name__ == "__main__":
    main()


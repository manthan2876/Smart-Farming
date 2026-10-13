"""Synchronize existing public.users to Supabase Auth (auth.users).

Uses the Supabase Admin Auth API with the Service Role Key to ensure all existing
users (admin, expert, farmer) exist in Supabase Auth with matching UUIDs.

Usage:
    python backend/scripts/migrate_users_to_supabase_auth.py --env dev
    python backend/scripts/migrate_users_to_supabase_auth.py --env prod
    python backend/scripts/migrate_users_to_supabase_auth.py --env both
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
from pathlib import Path

# Ensure backend root is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "src"))

for _d in glob.glob("/home/manthan/.cache/uv/archive-v0/*"):
    try:
        _items = set(os.listdir(_d))
        if "tests" not in _items and "numpy" not in _items and "cv2" not in _items:
            sys.path.append(_d)
    except OSError:
        pass

from dotenv import load_dotenv

load_dotenv(backend_dir / ".env")

import httpx
from sqlalchemy import text
from app.core.session import create_app_engine

DEFAULT_MIGRATION_PASSWORD = os.getenv("DEFAULT_USER_PASSWORD", "TemporaryPass123!")

ENV_CONFIGS = {
    "dev": {
        "label": "Development (smart-farming-dev)",
        "db_url": os.getenv("DATABASE_URL", ""),
        "supabase_url": os.getenv("DEV_SUPABASE_URL", "https://zgsbxzwyumvxazbroiws.supabase.co"),
        "service_role_key": os.getenv("DEV_SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
    },
    "prod": {
        "label": "Production (smart-farming)",
        "db_url": os.getenv("PROD_DATABASE_URL", ""),
        "supabase_url": os.getenv("PROD_SUPABASE_URL", "https://ntqevjzjhntkilmknrfh.supabase.co"),
        "service_role_key": os.getenv("PROD_SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
    },
}


def sanitize_db_url(url: str) -> str:
    if not url:
        return ""
    clean = url.strip().strip("'").strip('"')
    if clean.startswith("postgres://"):
        clean = "postgresql://" + clean[len("postgres://"):]
    return clean


def sync_users_for_env(env_name: str) -> bool:
    cfg = ENV_CONFIGS.get(env_name)
    if not cfg:
        print(f"[ERROR] Unknown environment: {env_name}")
        return False

    print("\n" + "=" * 65)
    print(f"  SYNCING USERS TO SUPABASE AUTH: {cfg['label']}")
    print("=" * 65)

    db_url = sanitize_db_url(cfg["db_url"])
    supabase_url = cfg["supabase_url"].rstrip("/")
    service_key = cfg["service_role_key"]

    if not db_url or not service_key:
        print(f"[ERROR] Missing database URL or service role key for {env_name}.")
        return False

    # 1. Fetch users from public.users
    print(f"[INFO] Fetching records from public.users...")
    engine = create_app_engine(db_url)
    users = []
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, name, email, phone, role, language FROM public.users WHERE deleted_at IS NULL ORDER BY created_at ASC;")
        )
        for row in result.mappings():
            users.append(dict(row))

    print(f"[INFO] Found {len(users)} user(s) in public.users.")

    # 2. Fetch existing auth.users via Supabase Admin API
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }

    existing_auth_emails = {}
    existing_auth_ids = {}

    try:
        with httpx.Client(timeout=15.0) as client:
            list_resp = client.get(f"{supabase_url}/auth/v1/admin/users?per_page=100", headers=headers)
            if list_resp.status_code == 200:
                data = list_resp.json()
                auth_user_list = data.get("users", [])
                for u in auth_user_list:
                    existing_auth_emails[u.get("email")] = u.get("id")
                    existing_auth_ids[u.get("id")] = u.get("email")
                print(f"[INFO] Found {len(auth_user_list)} existing user(s) in Supabase Auth.")
            else:
                print(f"[WARN] Could not list existing auth users ({list_resp.status_code}): {list_resp.text}")
    except Exception as exc:
        print(f"[WARN] Error connecting to Supabase Auth API: {exc}")

    # 3. Migrate each user
    created_count = 0
    updated_count = 0
    skipped_count = 0

    with httpx.Client(timeout=15.0) as client:
        for u in users:
            uid = str(u["id"])
            email = u["email"]
            if not email:
                print(f"   [SKIP] User {uid} has no email.")
                skipped_count += 1
                continue

            metadata = {
                "name": u.get("name") or "",
                "phone": u.get("phone") or "",
                "role": u.get("role") or "farmer",
                "language": u.get("language") or "English",
            }

            if uid in existing_auth_ids:
                print(f"   [EXISTS] User {email} ({uid}) already in Supabase Auth. Updating metadata...")
                update_resp = client.put(
                    f"{supabase_url}/auth/v1/admin/users/{uid}",
                    headers=headers,
                    json={"user_metadata": metadata, "email_confirm": True},
                )
                if update_resp.status_code == 200:
                    updated_count += 1
                else:
                    print(f"   [WARN] Update failed for {email}: {update_resp.text}")
            elif email in existing_auth_emails:
                print(f"   [NOTICE] User with email {email} exists with different ID ({existing_auth_emails[email]}). Updating metadata...")
                existing_id = existing_auth_emails[email]
                update_resp = client.put(
                    f"{supabase_url}/auth/v1/admin/users/{existing_id}",
                    headers=headers,
                    json={"user_metadata": metadata, "email_confirm": True},
                )
                if update_resp.status_code == 200:
                    updated_count += 1
            else:
                print(f"   [CREATE] Creating Supabase Auth user: {email} (ID: {uid})...")
                payload = {
                    "id": uid,
                    "email": email,
                    "password": DEFAULT_MIGRATION_PASSWORD,
                    "email_confirm": True,
                    "user_metadata": metadata,
                }
                create_resp = client.post(
                    f"{supabase_url}/auth/v1/admin/users",
                    headers=headers,
                    json=payload,
                )
                if create_resp.status_code in (200, 201):
                    print(f"   [SUCCESS] Created auth user: {email}")
                    created_count += 1
                else:
                    print(f"   [ERROR] Failed to create {email}: {create_resp.status_code} - {create_resp.text}")

    print(f"\n[SUMMARY] {cfg['label']}:")
    print(f"   - Created: {created_count}")
    print(f"   - Updated: {updated_count}")
    print(f"   - Skipped: {skipped_count}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Sync public.users to Supabase Auth")
    parser.add_argument("--env", choices=["dev", "prod", "both"], default="both", help="Target environment")
    args = parser.parse_args()

    if args.env in ("dev", "both"):
        sync_users_for_env("dev")
    if args.env in ("prod", "both"):
        sync_users_for_env("prod")


if __name__ == "__main__":
    main()

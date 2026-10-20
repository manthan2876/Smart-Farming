"""Synchronize existing public.users to Supabase Auth (auth.users).

Uses the Supabase Admin Auth API with the Service Role Key to ensure all existing
users (admin, expert, farmer) exist in Supabase Auth with matching UUIDs.

Usage:
    python backend/scripts/migrate_users_to_supabase_auth.py --env dev
    python backend/scripts/migrate_users_to_supabase_auth.py --env prod --yes
"""

from __future__ import annotations

import argparse
import secrets
import sys
from pathlib import Path

# Setup paths via _common
scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts_dir))

from _common import confirm_prod_action, get_supabase_env_config
import httpx
from sqlalchemy import text
from app.core.session import create_app_engine


def fetch_all_supabase_auth_users(supabase_url: str, service_key: str) -> tuple[dict[str, str], dict[str, str]]:
    """Paginate through all auth.users in Supabase to build email and ID lookup maps."""
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }
    existing_emails: dict[str, str] = {}
    existing_ids: dict[str, str] = {}
    page = 1
    per_page = 100

    with httpx.Client(timeout=20.0) as client:
        while True:
            resp = client.get(
                f"{supabase_url}/auth/v1/admin/users?page={page}&per_page={per_page}",
                headers=headers,
            )
            if resp.status_code != 200:
                print(f"[WARN] Could not list auth users page {page} ({resp.status_code}): {resp.text}")
                break

            data = resp.json()
            users = data.get("users", [])
            for u in users:
                email = u.get("email")
                uid = u.get("id")
                if email and uid:
                    existing_emails[email] = uid
                    existing_ids[uid] = email

            if len(users) < per_page:
                break
            page += 1

    return existing_emails, existing_ids


def sync_users_for_env(env_name: str) -> bool:
    cfg = get_supabase_env_config(env_name)
    db_url = cfg["db_url"]
    supabase_url = cfg["supabase_url"]
    service_key = cfg["service_role_key"]

    print("\n" + "=" * 65)
    print(f"  SYNCING USERS TO SUPABASE AUTH: {cfg['label']}")
    print("=" * 65)

    if not db_url or not service_key or not supabase_url:
        print(f"[ERROR] Missing database URL, Supabase URL, or service role key for {env_name}.")
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

    # 2. Paginate all existing auth.users
    print(f"[INFO] Discovering existing users in Supabase Auth...")
    existing_auth_emails, existing_auth_ids = fetch_all_supabase_auth_users(supabase_url, service_key)
    print(f"[INFO] Discovered {len(existing_auth_ids)} existing user(s) in Supabase Auth.")

    # 3. Synchronize users
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }

    created_count = 0
    updated_count = 0
    skipped_count = 0

    with httpx.Client(timeout=20.0) as client:
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
                print(f"   [EXISTS] User {email} ({uid}) exists. Updating metadata...")
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
                existing_id = existing_auth_emails[email]
                print(f"   [NOTICE] User {email} exists with ID {existing_id}. Updating metadata...")
                update_resp = client.put(
                    f"{supabase_url}/auth/v1/admin/users/{existing_id}",
                    headers=headers,
                    json={"user_metadata": metadata, "email_confirm": True},
                )
                if update_resp.status_code == 200:
                    updated_count += 1
            else:
                # Generate unique, cryptographically strong random password for security
                random_pass = f"Sf_{secrets.token_urlsafe(16)}!9"
                print(f"   [CREATE] Creating Supabase Auth user: {email} (ID: {uid})...")
                payload = {
                    "id": uid,
                    "email": email,
                    "password": random_pass,
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
    parser.add_argument(
        "--env",
        choices=["dev", "prod", "both"],
        default="dev",
        help="Target environment (defaults to dev)",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Bypass production confirmation prompt",
    )
    args = parser.parse_args()

    if args.env in ("prod", "both"):
        confirm_prod_action("Sync users to Production Supabase Auth", args.yes)

    if args.env in ("dev", "both"):
        sync_users_for_env("dev")
    if args.env in ("prod", "both"):
        sync_users_for_env("prod")


if __name__ == "__main__":
    main()

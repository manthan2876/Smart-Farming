"""Utility to synchronize or update a user's password in both PostgreSQL and Supabase Auth.

Updates:
  1. PostgreSQL public.users (Argon2 hash)
  2. Supabase Auth auth.users via Supabase Admin API (Service Role Key)

Usage:
  python backend/scripts/sync_user_password.py --email admin@smartfarming.com --env dev
  python backend/scripts/sync_user_password.py --email admin@smartfarming.com --env prod --yes
"""

from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

# Setup paths via _common
scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts_dir))

from _common import confirm_prod_action, get_supabase_env_config
import httpx
from sqlalchemy import text
from app.api.deps import hash_password
from app.core.session import create_app_engine


def sync_user_password(env_name: str, email: str, new_password: str) -> bool:
    cfg = get_supabase_env_config(env_name)
    db_url = cfg["db_url"]
    supabase_url = cfg["supabase_url"]
    service_key = cfg["service_role_key"]

    print("\n" + "=" * 65)
    print(f"  SYNCING PASSWORD FOR {email} on {cfg['label']}")
    print("=" * 65)

    if not db_url or not service_key or not supabase_url:
        print(f"[ERROR] Missing database URL, Supabase URL, or service role key for {env_name}.")
        return False

    # 1. Update PostgreSQL public.users with Argon2 hash
    print("[INFO] Updating PostgreSQL public.users...")
    engine = create_app_engine(db_url)
    argon2_hash = hash_password(new_password)

    user_id = None
    with engine.connect() as conn:
        with conn.begin():
            row = conn.execute(
                text("SELECT id FROM public.users WHERE lower(email) = lower(:email) AND deleted_at IS NULL;"),
                {"email": email},
            ).first()
            if not row:
                print(f"[ERROR] User with email '{email}' not found in public.users on {cfg['label']}.")
                return False
            user_id = str(row[0])

            conn.execute(
                text("UPDATE public.users SET password_hash = :hash, updated_at = now() WHERE id = :id;"),
                {"hash": argon2_hash, "id": user_id},
            )
            print(f"[SUCCESS] Updated PostgreSQL password_hash for user ID: {user_id}")

    # 2. Update Supabase Auth auth.users
    print("[INFO] Updating Supabase Auth auth.users...")
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=15.0) as client:
        # Check if user exists by ID directly
        resp = client.get(f"{supabase_url}/auth/v1/admin/users/{user_id}", headers=headers)
        target_id = user_id if resp.status_code == 200 else None

        # Fallback to email search if ID didn't match
        if not target_id:
            lookup = client.get(f"{supabase_url}/auth/v1/admin/users?per_page=50", headers=headers)
            if lookup.status_code == 200:
                for u in lookup.json().get("users", []):
                    if u.get("email") == email:
                        target_id = u.get("id")
                        break

        if not target_id:
            print(f"[ERROR] Could not find Supabase Auth user with email: {email}")
            return False

        resp = client.put(
            f"{supabase_url}/auth/v1/admin/users/{target_id}",
            headers=headers,
            json={"password": new_password, "email_confirm": True},
        )
        if resp.status_code in (200, 201):
            print(f"[SUCCESS] Updated Supabase Auth password for {email} (ID: {target_id})")
            return True
        else:
            print(f"[ERROR] Failed to update Supabase Auth password ({resp.status_code}): {resp.text}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Synchronize a user password to PostgreSQL and Supabase Auth.")
    parser.add_argument("--email", required=True, help="User email address")
    parser.add_argument("--env", choices=["dev", "prod", "both"], default="dev", help="Target environment")
    parser.add_argument("--yes", action="store_true", help="Bypass production confirmation prompt")
    args = parser.parse_args()

    # Always prompt securely via getpass to prevent shell history / ps snooping
    password = getpass.getpass(f"Enter new password for {args.email}: ")
    confirm = getpass.getpass("Confirm new password: ")
    if password != confirm:
        print("[ERROR] Passwords do not match.")
        sys.exit(1)

    targets = ["dev", "prod"] if args.env == "both" else [args.env]
    for env in targets:
        if env == "prod":
            confirm_prod_action(f"Update password for {args.email} on Production", args.yes)
        sync_user_password(env, args.email.strip().lower(), password)


if __name__ == "__main__":
    main()

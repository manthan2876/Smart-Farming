"""Utility to synchronize or update a user's password in both PostgreSQL and Supabase Auth.

Supports Dev, Prod, or both environments.
Updates:
  1. PostgreSQL public.users (Argon2 hash)
  2. Supabase Auth auth.users via Supabase Admin API (Service Role Key)

Usage:
  python backend/scripts/sync_user_password.py --email admin@smartfarming.com --env dev
  python backend/scripts/sync_user_password.py --email admin@smartfarming.com --password "MySecretPass!" --env both
"""

from __future__ import annotations

import argparse
import getpass
import glob
import os
import sys
from pathlib import Path

# Setup paths
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
from app.api.deps import hash_password
from app.core.session import create_app_engine

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


def sync_user_password(env_name: str, email: str, new_password: str) -> bool:
    cfg = ENV_CONFIGS.get(env_name)
    if not cfg:
        print(f"[ERROR] Unknown environment: {env_name}")
        return False

    print("\n" + "=" * 65)
    print(f"  SYNCING USER PASSWORD: {cfg['label']}")
    print("=" * 65)

    db_url = sanitize_db_url(cfg["db_url"])
    supabase_url = cfg["supabase_url"].rstrip("/")
    service_key = cfg["service_role_key"]

    if not db_url or not service_key:
        print(f"[ERROR] Missing database URL or service role key for {env_name}.")
        return False

    # 1. Update password in PostgreSQL public.users
    engine = create_app_engine(db_url)
    user_id = None
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT id FROM public.users WHERE email = :email AND deleted_at IS NULL"),
            {"email": email},
        ).mappings().first()
        if row:
            user_id = str(row["id"])
            new_hash = hash_password(new_password)
            conn.execute(
                text("UPDATE public.users SET password_hash = :hash WHERE id = :id"),
                {"hash": new_hash, "id": user_id},
            )
            conn.commit()
            print(f"[SUCCESS] Updated PostgreSQL password_hash for {email} (ID: {user_id})")
        else:
            print(f"[WARN] User {email} not found in PostgreSQL public.users.")

    # 2. Update password in Supabase Auth via Admin API
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=15.0) as client:
        # If user_id wasn't in public.users, look up by email in Supabase Auth
        target_id = user_id
        if not target_id:
            lookup = client.get(f"{supabase_url}/auth/v1/admin/users?per_page=100", headers=headers)
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
    parser.add_argument("--password", default=None, help="New password (prompted securely if omitted)")
    parser.add_argument("--env", choices=["dev", "prod", "both"], default="dev", help="Target environment")
    args = parser.parse_args()

    password = args.password
    if not password:
        password = getpass.getpass(f"Enter new password for {args.email}: ")
        confirm = getpass.getpass("Confirm new password: ")
        if password != confirm:
            print("[ERROR] Passwords do not match.")
            sys.exit(1)

    targets = ["dev", "prod"] if args.env == "both" else [args.env]
    for env in targets:
        sync_user_password(env, args.email.strip().lower(), password)


if __name__ == "__main__":
    main()


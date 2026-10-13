"""Execute Supabase Authentication triggers on Dev and Prod databases.

Installs public.handle_new_user() and on_auth_user_created trigger on auth.users
to automatically synchronize Supabase Auth users to public.users and provision
their Farm records.

Usage:
    python backend/scripts/setup_supabase_auth_triggers.py --all
    python backend/scripts/setup_supabase_auth_triggers.py --dev
    python backend/scripts/setup_supabase_auth_triggers.py --prod
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

from sqlalchemy import text
from app.core.session import create_app_engine


def sanitize_db_url(url: str) -> str:
    if not url:
        return ""
    clean = url.strip().strip("'").strip('"')
    if clean.startswith("postgres://"):
        clean = "postgresql://" + clean[len("postgres://"):]
    return clean


FUNCTION_SQL = """
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
DECLARE
  v_role text;
  v_name text;
  v_language text;
  v_farm_name text;
  v_location text;
BEGIN
  v_role := coalesce(new.raw_user_meta_data->>'role', 'farmer');
  v_name := coalesce(new.raw_user_meta_data->>'name', split_part(new.email, '@', 1));
  v_language := coalesce(new.raw_user_meta_data->>'language', 'English');
  v_location := coalesce(new.raw_user_meta_data->>'location', 'Gujarat, India');
  v_farm_name := coalesce(new.raw_user_meta_data->>'farm_name', (v_name || '''s Farm'));

  INSERT INTO public.users (
    id,
    email,
    phone,
    name,
    language,
    role,
    created_at
  )
  VALUES (
    new.id::text,
    new.email,
    new.phone,
    v_name,
    v_language,
    v_role,
    coalesce(new.created_at, now())
  )
  ON CONFLICT (id) DO UPDATE SET
    email = excluded.email,
    phone = coalesce(excluded.phone, public.users.phone),
    name = coalesce(excluded.name, public.users.name),
    role = coalesce(excluded.role, public.users.role);

  IF v_role = 'farmer' THEN
    INSERT INTO public.farms (
      user_id,
      name,
      location,
      area_acres,
      latitude,
      longitude,
      crop_history
    )
    VALUES (
      new.id::text,
      v_farm_name,
      v_location,
      nullif(new.raw_user_meta_data->>'farm_area_acres', '')::double precision,
      nullif(new.raw_user_meta_data->>'latitude', '')::double precision,
      nullif(new.raw_user_meta_data->>'longitude', '')::double precision,
      '[]'::json
    )
    ON CONFLICT (user_id) DO NOTHING;
  END IF;

  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
"""


def execute_sql_on_db(db_url: str, label: str) -> bool:
    print(f"\n[INFO] Connecting to {label}...")
    clean_url = sanitize_db_url(db_url)
    try:
        engine = create_app_engine(clean_url)
        with engine.connect() as conn:
            print("       1. Making users.password_hash nullable...")
            conn.execute(text("ALTER TABLE public.users ALTER COLUMN password_hash DROP NOT NULL;"))
            
            print("       2. Creating public.handle_new_user() trigger function...")
            conn.execute(text(FUNCTION_SQL))
            
            print("       3. Installing on_auth_user_created trigger on auth.users...")
            conn.execute(text("DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;"))
            conn.execute(text("CREATE TRIGGER on_auth_user_created AFTER INSERT OR UPDATE ON auth.users FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();"))
            
            conn.commit()
        print(f"[SUCCESS] Supabase auth triggers successfully installed on {label}!")
        return True
    except Exception as exc:
        print(f"[ERROR] Failed to install triggers on {label}: {exc}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Install Supabase auth triggers on Dev/Prod DB")
    parser.add_argument("--dev", action="store_true", help="Apply to Dev only")
    parser.add_argument("--prod", action="store_true", help="Apply to Prod only")
    parser.add_argument("--all", action="store_true", help="Apply to both Dev and Prod")
    args = parser.parse_args()

    dev_url = os.getenv("DATABASE_URL", "")
    prod_url = os.getenv("PROD_DATABASE_URL", "")

    if args.dev or args.all or (not args.prod and not args.dev and not args.all):
        if dev_url:
            execute_sql_on_db(dev_url, "Supabase Dev")
        else:
            print("[WARN] DATABASE_URL (Dev) not found in environment.")

    if args.prod or args.all:
        if prod_url:
            execute_sql_on_db(prod_url, "Supabase Prod")
        else:
            print("[WARN] PROD_DATABASE_URL (Prod) not found in environment.")


if __name__ == "__main__":
    main()


"""Supabase auth integration trigger & user provisioning.

Revision ID: 0003_supabase_auth_sync
Revises: 0002_password_reset
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0003_supabase_auth_sync"
down_revision = "0002_password_reset"
branch_labels = None
depends_on = None

SQL_CREATE_FUNCTION = """
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
DECLARE
  v_role text;
  v_name text;
  v_language text;
  v_farm_name text;
  v_location text;
BEGIN
  -- Security guard: Read role strictly from server-controlled raw_app_meta_data.
  -- Client-controlled raw_user_meta_data can NEVER set role to expert or admin.
  v_role := coalesce(new.raw_app_meta_data->>'role', 'farmer');
  IF v_role NOT IN ('farmer', 'expert', 'admin') THEN
    v_role := 'farmer';
  END IF;

  v_name := coalesce(new.raw_user_meta_data->>'name', split_part(new.email, '@', 1));
  v_language := coalesce(new.raw_user_meta_data->>'language', 'English');
  v_location := coalesce(new.raw_user_meta_data->>'location', 'Gujarat, India');
  v_farm_name := coalesce(new.raw_user_meta_data->>'farm_name', (v_name || '''s Farm'));

  -- Insert public.users. Do NOT overwrite existing user role on conflict.
  INSERT INTO public.users (
    id, email, phone, name, language, role, created_at
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
    name = coalesce(excluded.name, public.users.name);

  -- Provision initial Farm record for farmers
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
$$;
"""

SQL_CREATE_TRIGGER = """
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
"""


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    inspector = inspect(bind)
    tables = inspector.get_table_names(schema="public")

    # 1. Ensure password_hash is nullable in public.users if table exists
    if "users" in tables:
        op.execute("ALTER TABLE public.users ALTER COLUMN password_hash DROP NOT NULL;")

    # 2. Install hardened trigger function
    op.execute(SQL_CREATE_FUNCTION)

    # 3. If auth.users exists (e.g. Supabase managed database), install trigger
    has_auth_users = False
    try:
        has_auth_users = bool(
            bind.execute(
                sa.text(
                    "SELECT 1 FROM information_schema.tables WHERE table_schema = 'auth' AND table_name = 'users';"
                )
            ).scalar()
        )
    except Exception:
        has_auth_users = False

    if has_auth_users:
        op.execute(SQL_CREATE_TRIGGER)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    try:
        has_auth_users = bool(
            bind.execute(
                sa.text(
                    "SELECT 1 FROM information_schema.tables WHERE table_schema = 'auth' AND table_name = 'users';"
                )
            ).scalar()
        )
        if has_auth_users:
            op.execute("DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;")
    except Exception:
        pass

    op.execute("DROP FUNCTION IF EXISTS public.handle_new_user();")


"""Utility to sync/pull data from Supabase (Production) to Development (Aiven PostgreSQL or local SQLite)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "src"))

from dotenv import load_dotenv

load_dotenv(backend_dir / ".env")

from sqlalchemy import inspect, text
from app.core import Base
from app.core.session import create_app_engine, sanitize_db_url
import app.models  # Register all models with Base.metadata


def sync_prod_to_dev(force_sqlite: bool = False):
    prod_url = sanitize_db_url(os.getenv("PROD_DATABASE_URL"))

    if force_sqlite:
        sqlite_path = backend_dir / "dev_database.db"
        target_url = f"sqlite:///{sqlite_path.as_posix()}"
        target_label = f"Local SQLite ({sqlite_path.name})"
    else:
        target_url = sanitize_db_url(os.getenv("DATABASE_URL") or "sqlite:///./dev_database.db")
        target_label = "Development Database (Aiven)" if "postgres" in target_url else "Development Database"

    print("=" * 65)
    print("  SMART FARMING: PULLING PRODUCTION DATA INTO DEVELOPMENT")
    print("=" * 65)
    print(f"  Source (Production)  : {prod_url.split('@')[-1] if '@' in prod_url else prod_url}")
    print(f"  Target ({target_label}): {target_url.split('@')[-1] if '@' in target_url else target_url}")
    print("=" * 65)

    prod_engine = create_app_engine(prod_url)
    target_engine = create_app_engine(target_url)

    # 1. Verify connections
    print("\n[INFO] Connecting to Production Database (Supabase)...")
    with prod_engine.connect() as conn:
        conn.execute(text("SELECT 1;"))
    print("[SUCCESS] Connected to Production.")

    print(f"[INFO] Connecting to {target_label}...")
    with target_engine.connect() as conn:
        conn.execute(text("SELECT 1;"))
    print(f"[SUCCESS] Connected to {target_label}.")

    # 2. Ensure schema exists in target
    print(f"\n[INFO] Ensuring schema exists in {target_label}...")
    Base.metadata.create_all(target_engine)
    print("[SUCCESS] Schema verified.")

    prod_insp = inspect(prod_engine)
    prod_tables = [t for t in prod_insp.get_table_names() if t != "alembic_version"]

    target_insp = inspect(target_engine)
    target_tables = set(target_insp.get_table_names())

    print(f"\n[INFO] Found {len(prod_tables)} table(s) in Production to pull.")

    is_postgres_target = "postgres" in target_url

    with target_engine.connect() as target_conn:
        if is_postgres_target:
            try:
                target_conn.execute(text("SET session_replication_role = 'replica';"))
                target_conn.commit()
            except Exception:
                pass
        else:
            target_conn.execute(text("PRAGMA foreign_keys = OFF;"))

        total_synced = 0
        for table in sorted(prod_tables):
            if table not in target_tables:
                print(f"   [SKIP] Table '{table}' does not exist in target metadata.")
                continue

            # Read from Production
            with prod_engine.connect() as prod_conn:
                rows = prod_conn.execute(text(f'SELECT * FROM "{table}";')).mappings().all()

            # Clear target table
            target_conn.execute(text(f'DELETE FROM "{table}";'))

            if not rows:
                print(f"   - {table}: 0 rows (empty)")
                continue

            sanitized_rows = []
            for row in rows:
                row_dict = dict(row)
                if not is_postgres_target:
                    for k, v in row_dict.items():
                        if isinstance(v, (dict, list)):
                            row_dict[k] = json.dumps(v)
                sanitized_rows.append(row_dict)

            cols = list(sanitized_rows[0].keys())
            col_names = ", ".join([f'"{c}"' for c in cols])
            val_placeholders = ", ".join([f":{c}" for c in cols])
            insert_stmt = text(f'INSERT INTO "{table}" ({col_names}) VALUES ({val_placeholders});')

            for r in sanitized_rows:
                target_conn.execute(insert_stmt, r)

            target_conn.commit()
            print(f"   - {table}: synced {len(sanitized_rows)} row(s)")
            total_synced += len(sanitized_rows)

        if is_postgres_target:
            try:
                target_conn.execute(text("SET session_replication_role = 'DEFAULT';"))
                target_conn.commit()
            except Exception:
                pass
        else:
            target_conn.execute(text("PRAGMA foreign_keys = ON;"))
            target_conn.commit()

    print("\n" + "=" * 65)
    print(f"[SUCCESS] Database pull complete! Total rows imported: {total_synced}")
    print(f"Target ({target_label}) is now fully synced with Production!")
    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pull data from Production (Supabase) to Development")
    parser.add_argument("--sqlite", action="store_true", help="Force pulling into local SQLite dev_database.db instead of Aiven")
    args = parser.parse_args()
    sync_prod_to_dev(force_sqlite=args.sqlite)

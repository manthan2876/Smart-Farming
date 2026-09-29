"""One-time utility to sync/pull data from Supabase to local SQLite (dev_database.db)."""

import os
import sys
import json
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "src"))

from dotenv import load_dotenv

load_dotenv(backend_dir / ".env")

from sqlalchemy import create_engine, inspect, text
from app.core import Base
from app.core.session import sanitize_db_url
import app.models  # Register all models with Base.metadata


def sync_supabase_to_local_sqlite():
    prod_url = sanitize_db_url(os.getenv("PROD_DATABASE_URL"))
    sqlite_path = backend_dir / "dev_database.db"
    local_url = f"sqlite:///{sqlite_path.as_posix()}"

    print("=" * 65)
    print("  SMART FARMING: PULLING SUPABASE DATA INTO LOCAL SQLITE")
    print("=" * 65)
    print(f"  Source (Supabase) : {prod_url.split('@')[-1]}")
    print(f"  Target (Local DB) : {sqlite_path}")
    print("=" * 65)

    prod_engine = create_engine(prod_url)
    local_engine = create_engine(local_url)

    # 1. Verify source connection
    print("\n[INFO] Connecting to Supabase...")
    with prod_engine.connect() as conn:
        conn.execute(text("SELECT 1;"))
    print("[SUCCESS] Connected to Supabase.")

    # 2. Ensure schema exists in SQLite
    print("\n[INFO] Initializing tables in local SQLite...")
    Base.metadata.create_all(local_engine)
    print("[SUCCESS] Schema ready in local SQLite.")

    prod_insp = inspect(prod_engine)
    prod_tables = [t for t in prod_insp.get_table_names() if t != "alembic_version"]

    local_insp = inspect(local_engine)
    local_tables = set(local_insp.get_table_names())

    print(f"\n[INFO] Found {len(prod_tables)} table(s) in Supabase to sync.")

    with local_engine.connect() as local_conn:
        local_conn.execute(text("PRAGMA foreign_keys = OFF;"))

        total_synced = 0
        for table in sorted(prod_tables):
            if table not in local_tables:
                print(f"   [SKIP] Table '{table}' does not exist in local SQLite metadata.")
                continue

            # Read from Supabase
            with prod_engine.connect() as prod_conn:
                rows = prod_conn.execute(text(f'SELECT * FROM "{table}";')).mappings().all()

            # Clear local table
            local_conn.execute(text(f'DELETE FROM "{table}";'))

            if not rows:
                print(f"   - {table}: 0 rows (empty)")
                continue

            # Convert PostgreSQL types to SQLite-compatible values
            sanitized_rows = []
            for row in rows:
                row_dict = dict(row)
                for k, v in row_dict.items():
                    if isinstance(v, (dict, list)):
                        row_dict[k] = json.dumps(v)
                sanitized_rows.append(row_dict)

            cols = list(sanitized_rows[0].keys())
            col_names = ", ".join([f'"{c}"' for c in cols])
            val_placeholders = ", ".join([f":{c}" for c in cols])
            insert_stmt = text(f'INSERT INTO "{table}" ({col_names}) VALUES ({val_placeholders});')

            for r in sanitized_rows:
                local_conn.execute(insert_stmt, r)

            local_conn.commit()
            print(f"   - {table}: synced {len(sanitized_rows)} row(s)")
            total_synced += len(sanitized_rows)

        local_conn.execute(text("PRAGMA foreign_keys = ON;"))
        local_conn.commit()

    print("\n" + "=" * 65)
    print(f"[SUCCESS] Database sync complete! Total rows imported: {total_synced}")
    print(f"Local database updated at: {sqlite_path}")
    print("=" * 65)


if __name__ == "__main__":
    sync_supabase_to_local_sqlite()

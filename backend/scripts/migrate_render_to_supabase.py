"""Database Migration Script: Render PostgreSQL -> Supabase PostgreSQL.

Usage:
    python backend/scripts/migrate_render_to_supabase.py \\
        --source "postgresql://user:pass@source_host:5432/dbname?sslmode=require" \\
        --target "postgresql://user:pass@target_host:5432/dbname?sslmode=require"

Or via environment variables:
    SOURCE_DATABASE_URL="..." TARGET_DATABASE_URL="..." python backend/scripts/migrate_render_to_supabase.py
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "src"))

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from alembic import command
from alembic.config import Config
from app.core import Base
from app.core.session import create_app_engine
import app.models  # Ensure all models are registered in Base.metadata


def get_tables_and_counts(conn) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tables = [r[0] for r in cur.fetchall()]
        counts: dict[str, int] = {}
        for t in tables:
            cur.execute(f'SELECT count(*) FROM "{t}";')
            counts[t] = cur.fetchone()[0]
        return counts


def ensure_supabase_schema(target_url: str) -> bool:
    print("\n--- Step 1: Initializing Schema on Target Database ---")
    try:
        engine = create_app_engine(target_url)
        Base.metadata.create_all(engine)
        print("SQLAlchemy Base.metadata.create_all completed successfully.")

        # Run Alembic upgrade head
        os.environ["DATABASE_URL"] = target_url
        alembic_cfg = Config(str(backend_dir / "alembic.ini"))
        alembic_cfg.set_main_option("script_location", str(backend_dir / "alembic"))
        command.upgrade(alembic_cfg, "head")
        print("Alembic upgrade head completed successfully.")
        return True
    except Exception as exc:
        print(f"Error ensuring schema: {exc}")
        return False


def migrate_data(source_url: str, target_url: str) -> bool:
    print("\n--- Step 2: Migrating Records from Source to Target ---")
    # Clean psycopg2 URLs
    src_clean = source_url.replace("postgresql+psycopg2://", "postgresql://").replace("postgresql+psycopg://", "postgresql://")
    tgt_clean = target_url.replace("postgresql+psycopg2://", "postgresql://").replace("postgresql+psycopg://", "postgresql://")

    r_conn = psycopg2.connect(src_clean)
    s_conn = psycopg2.connect(tgt_clean)

    r_cur = r_conn.cursor(cursor_factory=RealDictCursor)
    s_cur = s_conn.cursor()

    source_counts = get_tables_and_counts(r_conn)
    print("Source Tables and Row Counts:")
    for t, c in source_counts.items():
        print(f"  {t}: {c} rows")

    target_counts_initial = get_tables_and_counts(s_conn)
    print("\nTarget Tables before migration:")
    for t, c in target_counts_initial.items():
        print(f"  {t}: {c} rows")

    # Disable foreign key constraint triggers temporarily
    print("\nSetting session_replication_role = 'replica' on Target...")
    s_cur.execute("SET session_replication_role = 'replica';")
    s_conn.commit()

    tables_to_migrate = [t for t in source_counts.keys() if t != "alembic_version"]

    # Sync alembic_version if present
    if "alembic_version" in source_counts and source_counts["alembic_version"] > 0:
        r_cur.execute("SELECT version_num FROM alembic_version;")
        r_ver = r_cur.fetchone()
        if r_ver:
            s_cur.execute("DELETE FROM alembic_version;")
            s_cur.execute("INSERT INTO alembic_version (version_num) VALUES (%s);", (r_ver["version_num"],))
            s_conn.commit()
            print(f"Synced alembic_version: {r_ver['version_num']}")

    print("\nTruncating target tables before data load...")
    for table in tables_to_migrate:
        s_cur.execute(f'TRUNCATE TABLE "{table}" CASCADE;')
    s_conn.commit()

    total_migrated_rows = 0
    for table in tables_to_migrate:
        row_count = source_counts[table]
        if row_count == 0:
            print(f"Skipping {table} (0 rows)")
            continue

        print(f"\nMigrating {table} ({row_count} rows)...")
        r_cur.execute(f'SELECT * FROM "{table}";')
        rows = r_cur.fetchall()
        if not rows:
            continue

        columns = list(rows[0].keys())
        col_names = ", ".join([f'"{c}"' for c in columns])
        placeholders = ", ".join(["%s"] * len(columns))
        insert_query = f'INSERT INTO "{table}" ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING;'

        batch_size = 500
        values = []

        def adapt_val(val):
            if isinstance(val, (dict, list)):
                return Json(val)
            return val

        for row in rows:
            values.append(tuple(adapt_val(row[c]) for c in columns))
            if len(values) >= batch_size:
                s_cur.executemany(insert_query, values)
                values = []
        if values:
            s_cur.executemany(insert_query, values)

        s_conn.commit()
        print(f"  Inserted {len(rows)} rows into {table}.")
        total_migrated_rows += len(rows)

    # Reset sequences for auto-increment columns
    print("\n--- Step 3: Resetting PostgreSQL Sequences ---")
    s_cur.execute("""
        SELECT table_name, column_name, column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' 
          AND column_default LIKE 'nextval%';
    """)
    sequences = s_cur.fetchall()
    for table_name, col_name, col_def in sequences:
        try:
            seq_name = col_def.split("'")[1]
            s_cur.execute(f"""
                SELECT setval('{seq_name}', COALESCE((SELECT MAX("{col_name}") FROM "{table_name}"), 1), true);
            """)
            print(f"  Reset sequence {seq_name} for {table_name}.{col_name}")
        except Exception as e:
            print(f"  Warning resetting sequence for {table_name}.{col_name}: {e}")
    s_conn.commit()

    # Re-enable foreign key checks
    print("\nRe-enabling foreign key checks (session_replication_role = 'origin')...")
    s_cur.execute("SET session_replication_role = 'origin';")
    s_conn.commit()

    # Final verification
    print("\n--- Step 4: Verification ---")
    target_counts_final = get_tables_and_counts(s_conn)
    all_match = True
    for t in source_counts.keys():
        r_cnt = source_counts.get(t, 0)
        s_cnt = target_counts_final.get(t, 0)
        status = "MATCH" if r_cnt == s_cnt else "MISMATCH"
        if r_cnt != s_cnt:
            all_match = False
        print(f"  {t}: Source={r_cnt}, Target={s_cnt} -> {status}")

    r_conn.close()
    s_conn.close()

    if all_match:
        print(f"\nMIGRATION SUCCESSFUL! All {total_migrated_rows} rows transferred and verified.")
        return True
    else:
        print("\nWARNING: Some table counts did not match.")
        return False


def main():
    parser = argparse.ArgumentParser(description="Migrate PostgreSQL database from Render to Supabase.")
    parser.add_argument("--source", default=os.getenv("SOURCE_DATABASE_URL") or os.getenv("RENDER_DATABASE_URL"), help="Source PostgreSQL connection URL")
    parser.add_argument("--target", default=os.getenv("TARGET_DATABASE_URL") or os.getenv("SUPABASE_DATABASE_URL"), help="Target PostgreSQL connection URL")

    args = parser.parse_args()

    if not args.source or not args.target:
        print("Error: Both --source and --target database URLs must be provided via arguments or environment variables.")
        sys.exit(1)

    if not ensure_supabase_schema(args.target):
        print("Schema creation failed. Aborting.")
        sys.exit(1)

    if not migrate_data(args.source, args.target):
        print("Data migration failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()

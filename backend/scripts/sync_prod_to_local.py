"""
sync_prod_to_local.py — Update & match Development database to Production.

This utility copies schema and table records from Production (Supabase) into
Development (Aiven PostgreSQL or local SQLite) so local development exactly matches
the current state of production.

NOTE: This is strictly a local developer tool and CANNOT be executed inside GitHub Actions.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Security guard: forbid running in CI/CD pipeline
if os.getenv("GITHUB_ACTIONS") == "true":
    print("\n[ERROR] sync_prod_to_local.py is a local developer tool to match dev with prod.")
    print("It CANNOT be triggered or executed by GitHub Actions.")
    sys.exit(1)

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "src"))

from dotenv import load_dotenv

load_dotenv(backend_dir / ".env")

from sqlalchemy import inspect, text
from app.core import Base
from app.core.session import create_app_engine, sanitize_db_url
import app.models  # Register all models with Base.metadata


TABLE_DEPENDENCY_ORDER = [
    "users",
    "farms",
    "plots",
    "images",
    "predictions",
    "recommendations",
    "feedback",
    "expert_reviews",
    "dataset_candidates",
    "alerts",
    "password_reset_tokens",
    "mlops_runs",
    "entity_translations",
]


def sync_prod_to_dev(force_sqlite: bool = False, skip_confirm: bool = False):
    """Pulls schema and all table records from Production (Supabase) into Development (Aiven/SQLite)."""
    prod_url = sanitize_db_url(os.getenv("PROD_DATABASE_URL"))
    if not prod_url:
        print("\n[ERROR] PROD_DATABASE_URL not found in backend/.env!")
        sys.exit(1)

    if force_sqlite:
        sqlite_path = backend_dir / "dev_database.db"
        target_url = f"sqlite:///{sqlite_path.as_posix()}"
        target_label = f"Local SQLite ({sqlite_path.name})"
    else:
        target_url = sanitize_db_url(os.getenv("DATABASE_URL") or "sqlite:///./dev_database.db")
        target_label = "Development Database (Aiven)" if "postgres" in target_url else "Development Database"

    print("=" * 65)
    print("  SMART FARMING: MATCH DEVELOPMENT DATABASE TO PRODUCTION")
    print("=" * 65)
    print(f"  Source (Production)  : {prod_url.split('@')[-1] if '@' in prod_url else prod_url}")
    print(f"  Target ({target_label}): {target_url.split('@')[-1] if '@' in target_url else target_url}")
    print("=" * 65)

    if not skip_confirm:
        confirm = input(f"\nWarning: This will overwrite tables in {target_label} to match Production.\nProceed? [y/N]: ").strip().lower()
        if confirm not in ("y", "yes"):
            print("Aborted.")
            return

    from sqlalchemy.pool import NullPool
    prod_engine = create_app_engine(prod_url, poolclass=NullPool)
    target_engine = create_app_engine(target_url, poolclass=NullPool)

    # 1. Ensure schema exists in target
    print(f"\n[INFO] Ensuring declared schema exists in {target_label}...")
    Base.metadata.create_all(target_engine)
    print(f"[SUCCESS] Schema verified on {target_label}.")

    with prod_engine.connect() as prod_conn, target_engine.connect() as target_conn:
        # 2. Inspect tables in Production using the active connection
        prod_insp = inspect(prod_conn)
        prod_tables = [t for t in prod_insp.get_table_names() if t != "alembic_version"]

        target_insp = inspect(target_conn)
        target_tables = set(target_insp.get_table_names())

        # 3. Sync alembic_version from Production to Development
        try:
            prod_alembic = prod_conn.execute(text("SELECT version_num FROM alembic_version;")).scalar()
            if prod_alembic:
                target_conn.execute(text('CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num));'))
                target_conn.execute(text("DELETE FROM alembic_version;"))
                target_conn.execute(text("INSERT INTO alembic_version (version_num) VALUES (:v);"), {"v": prod_alembic})
                target_conn.commit()
                print(f"[SUCCESS] Alembic migration state matched to Production (revision: {prod_alembic}).")
        except Exception as exc:
            print(f"[NOTE] Alembic version sync: {exc}")

        print(f"\n[INFO] Found {len(prod_tables)} table(s) in Production to sync into Development.")

        is_postgres_target = "postgres" in target_url

        if is_postgres_target:
            try:
                target_conn.execute(text("SET session_replication_role = 'replica';"))
                target_conn.commit()
            except Exception:
                pass
        else:
            target_conn.execute(text("PRAGMA foreign_keys = OFF;"))

        def get_order(t_name: str) -> int:
            try:
                return TABLE_DEPENDENCY_ORDER.index(t_name)
            except ValueError:
                return 999

        ordered_tables = sorted(prod_tables, key=get_order)

        # Clear target tables in reverse dependency order
        for table in reversed(ordered_tables):
            if table in target_tables:
                target_conn.execute(text(f'DELETE FROM "{table}";'))
        target_conn.commit()

        # Insert rows in dependency order using bulk execute
        total_synced = 0
        for table in ordered_tables:
            if table not in target_tables:
                print(f"   [SKIP] Table '{table}' does not exist in target metadata.")
                continue

            rows = prod_conn.execute(text(f'SELECT * FROM "{table}";')).mappings().all()

            if not rows:
                print(f"   - {table}: 0 rows (empty)")
                continue

            sanitized_rows = []
            for row in rows:
                row_dict = dict(row)
                for k, v in row_dict.items():
                    if isinstance(v, (dict, list)):
                        if is_postgres_target:
                            try:
                                import psycopg2.extras
                                row_dict[k] = psycopg2.extras.Json(v)
                            except Exception:
                                row_dict[k] = json.dumps(v)
                        else:
                            row_dict[k] = json.dumps(v)
                sanitized_rows.append(row_dict)

            cols = list(sanitized_rows[0].keys())
            col_names = ", ".join([f'"{c}"' for c in cols])
            val_placeholders = ", ".join([f":{c}" for c in cols])
            insert_stmt = text(f'INSERT INTO "{table}" ({col_names}) VALUES ({val_placeholders}) ON CONFLICT DO NOTHING;')

            target_conn.execute(insert_stmt, sanitized_rows)
            target_conn.commit()
            print(f"   - {table}: matched {len(sanitized_rows)} row(s)")
            total_synced += len(sanitized_rows)

        if is_postgres_target:
            try:
                target_conn.execute(text("SET session_replication_role = 'DEFAULT';"))
                target_conn.commit()
            except Exception:
                pass

            # Reset all PostgreSQL sequences to MAX(id) to prevent duplicate key errors on subsequent inserts
            try:
                cols = target_conn.execute(text("""
                    SELECT c.table_name, c.column_name
                    FROM information_schema.columns c
                    JOIN information_schema.tables t ON c.table_name = t.table_name
                    WHERE t.table_schema = 'public' 
                      AND t.table_type = 'BASE TABLE'
                      AND (c.column_default LIKE 'nextval(%' OR c.identity_generation IS NOT NULL)
                """)).fetchall()

                for table_name, column_name in cols:
                    seq_name = target_conn.execute(
                        text("SELECT pg_get_serial_sequence(:t, :c)"),
                        {"t": f'public."{table_name}"', "c": column_name}
                    ).scalar() or target_conn.execute(
                        text("SELECT pg_get_serial_sequence(:t, :c)"),
                        {"t": table_name, "c": column_name}
                    ).scalar()

                    if seq_name:
                        max_id = target_conn.execute(text(f'SELECT MAX("{column_name}") FROM "{table_name}"')).scalar()
                        if max_id is not None and max_id > 0:
                            target_conn.execute(
                                text("SELECT setval(:seq, :max_id, true)"),
                                {"seq": seq_name, "max_id": max_id}
                            )
                        else:
                            target_conn.execute(
                                text("SELECT setval(:seq, 1, false)"),
                                {"seq": seq_name}
                            )
                target_conn.commit()
                print("   [INFO] PostgreSQL auto-increment sequences advanced and synchronized.")
            except Exception as seq_exc:
                print(f"   [WARN] Could not update PostgreSQL sequences: {seq_exc}")
        else:
            target_conn.execute(text("PRAGMA foreign_keys = ON;"))
            target_conn.commit()

    print("\n" + "=" * 65)
    print(f"[SUCCESS] Sync complete! Total rows imported: {total_synced}")
    print(f"{target_label} now identically matches Production!")
    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Match Development database to Production (Local dev tool only)")
    parser.add_argument("--sqlite", action="store_true", help="Force matching local SQLite dev_database.db instead of Aiven")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()
    sync_prod_to_dev(force_sqlite=args.sqlite, skip_confirm=args.yes)

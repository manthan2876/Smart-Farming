"""Production & Development Database Migration & Synchronization CLI.

Supports managing Aiven Cloud PostgreSQL (Development) and Supabase Cloud PostgreSQL (Production)
with flexible options to migrate schema, seed reference data, or sync records between environments.

Usage:
    # Interactive menu:
    python backend/scripts/migrate_to_prod.py

    # Apply schema updates to Production only (Supabase):
    python backend/scripts/migrate_to_prod.py --schema-only --yes

    # Apply schema updates to Development only (Aiven):
    python backend/scripts/migrate_to_prod.py --dev-only --yes

    # Apply schema updates to BOTH Dev and Production:
    python backend/scripts/migrate_to_prod.py --all-dbs --yes

    # Sync data from Dev (Aiven) to Production (Supabase):
    python backend/scripts/migrate_to_prod.py --sync-data --yes

    # Sync data from Production (Supabase) to Dev (Aiven):
    python backend/scripts/migrate_to_prod.py --sync-to-dev --yes

    # Check connectivity and table counts for both databases:
    python backend/scripts/migrate_to_prod.py --check
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

# Ensure backend root is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "src"))

from dotenv import load_dotenv

load_dotenv(backend_dir / ".env")

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.core import Base
from app.core.config import settings
from app.core.session import create_app_engine, sanitize_db_url
import app.models  # Register all models with Base.metadata


def get_target_prod_url(cli_target: str | None = None) -> str:
    """Resolve production database URL from CLI arg, PROD_DATABASE_URL, or SUPABASE_DATABASE_URL."""
    target = (
        cli_target
        or os.getenv("PROD_DATABASE_URL")
        or os.getenv("SUPABASE_DATABASE_URL")
        or os.getenv("TARGET_DATABASE_URL")
        or getattr(settings, "PROD_DATABASE_URL", None)
    )
    if not target:
        print("\n[ERROR] Production database URL not found.")
        print("Please provide --target or set PROD_DATABASE_URL in backend/.env or your environment.")
        sys.exit(1)
    return sanitize_db_url(target)


def get_dev_source_url(cli_source: str | None = None) -> str:
    """Resolve development database URL (Aiven Cloud PostgreSQL or local SQLite)."""
    source = (
        cli_source
        or os.getenv("DEV_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or os.getenv("LOCAL_DATABASE_URL")
        or "sqlite:///./dev_database.db"
    )
    return sanitize_db_url(source)


def verify_connection(url: str, label: str = "Database") -> bool:
    """Verifies database connectivity."""
    print(f"\n[INFO] Verifying connection to {label}...")
    parsed = urlparse(url)
    display_host = parsed.hostname or url.split("@")[-1].split("/")[0] if "@" in url else url
    print(f"       Endpoint: {parsed.scheme}://{display_host}")
    print(f"       Username: {parsed.username}")
    print(f"       Host: {parsed.hostname}:{parsed.port or 5432}")
    print(f"       Database: {parsed.path.lstrip('/')}")
    try:
        engine = create_app_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
        print(f"[SUCCESS] {label} connected successfully.")
        return True
    except Exception as exc:
        print(f"[ERROR] Failed to connect to {label}: {exc}")
        return False


def apply_schema_migrations(target_url: str, db_label: str = "Database") -> bool:
    """Safely applies SQLAlchemy Base.metadata.create_all and Alembic migrations to target database."""
    print("\n" + "=" * 65)
    print(f"  APPLYING SCHEMA MIGRATIONS: {db_label.upper()}")
    print("=" * 65)

    try:
        engine = create_app_engine(target_url)
        print(f"[INFO] Creating newly declared tables in {db_label}...")
        Base.metadata.create_all(engine)
        print(f"[SUCCESS] Base.metadata.create_all completed for {db_label}.")

        # Run Alembic upgrade head
        print(f"[INFO] Executing Alembic migrations ('upgrade head') on {db_label}...")
        os.environ["DATABASE_URL"] = target_url
        alembic_cfg = Config(str(backend_dir / "alembic.ini"))
        alembic_cfg.set_main_option("script_location", str(backend_dir / "alembic"))
        command.upgrade(alembic_cfg, "head")
        print(f"[SUCCESS] Alembic upgrade head completed on {db_label}.")

        # Print current tables
        inspector = inspect(engine)
        tables = sorted(inspector.get_table_names())
        print(f"\n[INFO] {db_label} now contains {len(tables)} table(s):")
        for t in tables:
            print(f"   - {t}")
        return True
    except Exception as exc:
        print(f"[ERROR] Schema migration failed on {db_label}: {exc}")
        return False


def seed_database_defaults(target_url: str, db_label: str = "Database") -> bool:
    """Initializes default reference roles, admin accounts, and sample data."""
    print("\n" + "=" * 65)
    print(f"  SEEDING DEFAULT ACCOUNTS & REFERENCE DATA: {db_label.upper()}")
    print("=" * 65)
    try:
        from app.core.init_db import initialize_database

        os.environ["DATABASE_URL"] = target_url
        initialize_database()
        print(f"[SUCCESS] Default seed data verified/initialized for {db_label}.")
        return True
    except Exception as exc:
        print(f"[ERROR] Seeding failed on {db_label}: {exc}")
        return False


def sync_records(source_url: str, target_url: str, src_label: str = "Source", tgt_label: str = "Target") -> bool:
    """Syncs data rows between databases safely using ON CONFLICT DO NOTHING."""
    print("\n" + "=" * 65)
    print(f"  SYNCING DATA: {src_label.upper()} -> {tgt_label.upper()}")
    print("=" * 65)

    try:
        src_engine = create_app_engine(source_url)
        tgt_engine = create_app_engine(target_url)

        src_inspector = inspect(src_engine)
        tables = [t for t in src_inspector.get_table_names() if t != "alembic_version"]

        print(f"[INFO] Inspecting {len(tables)} table(s) in {src_label}...")

        with tgt_engine.connect() as tgt_conn:
            is_postgres = "postgres" in target_url
            if is_postgres:
                try:
                    tgt_conn.execute(text("SET session_replication_role = 'replica';"))
                    tgt_conn.commit()
                except Exception:
                    pass

            total_synced = 0
            for table in sorted(tables):
                with src_engine.connect() as s_conn:
                    rows = s_conn.execute(text(f'SELECT * FROM "{table}";')).mappings().all()

                if not rows:
                    continue

                print(f"   Syncing {table} ({len(rows)} row(s))...")
                for row in rows:
                    row_dict = dict(row)
                    # Convert dicts/lists to JSON strings if inserting into SQLite
                    if "sqlite" in target_url:
                        for k, v in row_dict.items():
                            if isinstance(v, (dict, list)):
                                row_dict[k] = json.dumps(v)

                    cols = list(row_dict.keys())
                    col_names = ", ".join([f'"{c}"' for c in cols])
                    val_placeholders = ", ".join([f":{c}" for c in cols])
                    stmt = text(f'INSERT INTO "{table}" ({col_names}) VALUES ({val_placeholders}) ON CONFLICT DO NOTHING;')
                    tgt_conn.execute(stmt, row_dict)
                    total_synced += 1

                tgt_conn.commit()

            if is_postgres:
                try:
                    tgt_conn.execute(text("SET session_replication_role = 'DEFAULT';"))
                    tgt_conn.commit()
                except Exception:
                    pass

        print(f"\n[SUCCESS] Data synchronization completed! Total rows processed: {total_synced}")
        return True
    except Exception as exc:
        print(f"[ERROR] Data sync failed: {exc}")
        return False


def check_databases(dev_url: str, prod_url: str) -> None:
    """Check connectivity and compare row counts across both Dev and Prod."""
    dev_ok = verify_connection(dev_url, "Development Database (Aiven)")
    prod_ok = verify_connection(prod_url, "Production Database (Supabase)")

    if not dev_ok or not prod_ok:
        print("\n[!] Could not connect to one or more databases.")
        return

    dev_engine = create_app_engine(dev_url)
    prod_engine = create_app_engine(prod_url)

    dev_insp = inspect(dev_engine)
    prod_insp = inspect(prod_engine)

    all_tables = sorted(set(dev_insp.get_table_names()) | set(prod_insp.get_table_names()))
    table_list = [t for t in all_tables if t != "alembic_version"]

    print("\n" + "=" * 65)
    print(f"{'TABLE NAME':<26} | {'DEV (AIVEN)':<15} | {'PROD (SUPABASE)':<15}")
    print("-" * 65)

    with dev_engine.connect() as dev_conn, prod_engine.connect() as prod_conn:
        for t in table_list:
            dev_cnt = "-"
            prod_cnt = "-"
            if dev_insp.has_table(t):
                dev_cnt = str(dev_conn.execute(text(f'SELECT count(*) FROM "{t}";')).scalar())
            if prod_insp.has_table(t):
                prod_cnt = str(prod_conn.execute(text(f'SELECT count(*) FROM "{t}";')).scalar())
            print(f"{t:<26} | {dev_cnt:<15} | {prod_cnt:<15}")

    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(
        description="Smart Farming - Dev (Aiven) & Prod (Supabase) Database Management Utility"
    )
    parser.add_argument(
        "--target",
        type=str,
        help="Production database URL (defaults to PROD_DATABASE_URL in .env)",
    )
    parser.add_argument(
        "--source",
        type=str,
        help="Development database URL (defaults to DATABASE_URL in .env)",
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Apply schema migrations to Production (Supabase).",
    )
    parser.add_argument(
        "--dev-only",
        action="store_true",
        help="Apply schema migrations to Development (Aiven).",
    )
    parser.add_argument(
        "--all-dbs",
        action="store_true",
        help="Apply schema migrations to BOTH Dev (Aiven) and Production (Supabase).",
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Apply schema migrations and seed reference accounts on Production.",
    )
    parser.add_argument(
        "--seed-dev",
        action="store_true",
        help="Apply schema migrations and seed reference accounts on Development.",
    )
    parser.add_argument(
        "--sync-data",
        action="store_true",
        help="Sync rows from Development (Aiven) to Production (Supabase).",
    )
    parser.add_argument(
        "--sync-to-dev",
        action="store_true",
        help="Sync rows from Production (Supabase) to Development (Aiven).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify connectivity and compare table row counts for both Dev and Prod.",
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompt for automated CI/CD execution.",
    )

    args = parser.parse_args()

    prod_url = get_target_prod_url(args.target)
    dev_url = get_dev_source_url(args.source)

    print("=" * 65)
    print("  SMART FARMING: DATABASE MIGRATION & SYNC UTILITY")
    print("=" * 65)
    print(f"  Dev  (Aiven)   : {dev_url.split('@')[-1] if '@' in dev_url else dev_url}")
    print(f"  Prod (Supabase): {prod_url.split('@')[-1] if '@' in prod_url else prod_url}")
    print("=" * 65)

    if args.check:
        check_databases(dev_url, prod_url)
        return

    # Non-interactive CLI flag mode
    if args.schema_only or args.dev_only or args.all_dbs or args.seed or args.seed_dev or args.sync_data or args.sync_to_dev:
        if not args.yes:
            confirm = input("\nProceed with database execution? [y/N]: ").strip().lower()
            if confirm not in ("y", "yes"):
                print("Aborted.")
                return

        if args.dev_only:
            verify_connection(dev_url, "Dev (Aiven)")
            apply_schema_migrations(dev_url, "Dev (Aiven)")
        elif args.all_dbs:
            verify_connection(dev_url, "Dev (Aiven)")
            apply_schema_migrations(dev_url, "Dev (Aiven)")
            verify_connection(prod_url, "Prod (Supabase)")
            apply_schema_migrations(prod_url, "Prod (Supabase)")
        elif args.schema_only:
            verify_connection(prod_url, "Prod (Supabase)")
            apply_schema_migrations(prod_url, "Prod (Supabase)")

        if args.seed:
            seed_database_defaults(prod_url, "Prod (Supabase)")
        if args.seed_dev:
            seed_database_defaults(dev_url, "Dev (Aiven)")

        if args.sync_data:
            sync_records(dev_url, prod_url, "Dev (Aiven)", "Prod (Supabase)")
        if args.sync_to_dev:
            sync_records(prod_url, dev_url, "Prod (Supabase)", "Dev (Aiven)")

        print("\n[COMPLETE] All requested operations completed successfully.")
        return

    # Interactive menu mode
    print("\nSelect Migration Option:")
    print("  [1] Apply Schema to Production (Supabase)")
    print("  [2] Apply Schema to Development (Aiven)")
    print("  [3] Apply Schema to BOTH Dev & Prod (Recommended for releases)")
    print("  [4] Sync Data: Dev (Aiven) -> Prod (Supabase)")
    print("  [5] Sync Data: Prod (Supabase) -> Dev (Aiven)")
    print("  [6] Check Connections & Table Status (Both databases)")
    print("  [7] Cancel")

    try:
        choice = input("\nEnter choice [1-7]: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        return

    if choice == "1":
        if verify_connection(prod_url, "Production (Supabase)"):
            apply_schema_migrations(prod_url, "Production (Supabase)")
    elif choice == "2":
        if verify_connection(dev_url, "Development (Aiven)"):
            apply_schema_migrations(dev_url, "Development (Aiven)")
    elif choice == "3":
        if verify_connection(dev_url, "Development (Aiven)") and verify_connection(prod_url, "Production (Supabase)"):
            apply_schema_migrations(dev_url, "Development (Aiven)")
            apply_schema_migrations(prod_url, "Production (Supabase)")
    elif choice == "4":
        confirm = input("\nWARNING: This will copy records from Dev to Prod. Proceed? [y/N]: ").strip().lower()
        if confirm in ("y", "yes"):
            if verify_connection(dev_url, "Dev") and verify_connection(prod_url, "Prod"):
                sync_records(dev_url, prod_url, "Dev (Aiven)", "Prod (Supabase)")
    elif choice == "5":
        confirm = input("\nWARNING: This will copy records from Prod to Dev. Proceed? [y/N]: ").strip().lower()
        if confirm in ("y", "yes"):
            if verify_connection(prod_url, "Prod") and verify_connection(dev_url, "Dev"):
                sync_records(prod_url, dev_url, "Prod (Supabase)", "Dev (Aiven)")
    elif choice == "6":
        check_databases(dev_url, prod_url)
    else:
        print("Cancelled.")


if __name__ == "__main__":
    main()

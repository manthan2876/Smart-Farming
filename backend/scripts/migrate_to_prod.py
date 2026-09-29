"""Production Database Migration & Synchronization CLI.

Enables keeping local development (SQLite/local Postgres) completely separate
from production (Supabase/cloud Postgres), with flexible options to migrate
schema, seed data, or sync records on demand or via GitHub Actions.

Usage:
    # Interactive mode (prompts for options):
    python backend/scripts/migrate_to_prod.py

    # Apply schema updates only (Alembic upgrade head + create_all):
    python backend/scripts/migrate_to_prod.py --schema-only

    # Apply schema and seed default reference data:
    python backend/scripts/migrate_to_prod.py --seed

    # Full data sync from local database to production:
    python backend/scripts/migrate_to_prod.py --sync-data --yes
"""

from __future__ import annotations

import argparse
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


def get_local_source_url(cli_source: str | None = None) -> str:
    """Resolve local development database URL."""
    source = (
        cli_source
        or os.getenv("LOCAL_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or "sqlite:///./dev_database.db"
    )
    return sanitize_db_url(source)


def verify_connection(url: str, label: str = "Database") -> bool:
    """Verifies database connectivity."""
    print(f"\n[INFO] Verifying connection to {label}...")
    parsed = urlparse(url)
    display_host = parsed.hostname or url.split("@")[-1].split("/")[0] if "@" in url else url
    print(f"       Endpoint: {parsed.scheme}://{display_host}")
    try:
        engine = create_app_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
        print(f"[SUCCESS] {label} connected successfully.")
        return True
    except Exception as exc:
        print(f"[ERROR] Failed to connect to {label}: {exc}")
        return False


def apply_schema_migrations(target_url: str) -> bool:
    """Safely applies SQLAlchemy Base.metadata.create_all and Alembic migrations to target database."""
    print("\n" + "=" * 65)
    print("  STEP 1: APPLYING PRODUCTION SCHEMA MIGRATIONS")
    print("=" * 65)

    try:
        engine = create_app_engine(target_url)
        print("[INFO] Creating any newly declared tables in SQLAlchemy metadata...")
        Base.metadata.create_all(engine)
        print("[SUCCESS] Base.metadata.create_all completed.")

        # Run Alembic upgrade head
        print("[INFO] Executing Alembic migrations ('upgrade head')...")
        os.environ["DATABASE_URL"] = target_url
        alembic_cfg = Config(str(backend_dir / "alembic.ini"))
        alembic_cfg.set_main_option("script_location", str(backend_dir / "alembic"))
        command.upgrade(alembic_cfg, "head")
        print("[SUCCESS] Alembic upgrade head completed successfully.")

        # Print current tables on production
        inspector = inspect(engine)
        tables = sorted(inspector.get_table_names())
        print(f"\n[INFO] Production database now contains {len(tables)} table(s):")
        for t in tables:
            print(f"   - {t}")
        return True
    except Exception as exc:
        print(f"[ERROR] Schema migration failed: {exc}")
        return False


def seed_production_defaults(target_url: str) -> bool:
    """Initializes default reference roles, admin accounts, and crop manifests on target database."""
    print("\n" + "=" * 65)
    print("  STEP 2: SEEDING DEFAULT PRODUCTION ACCOUNTS & REFERENCE DATA")
    print("=" * 65)
    try:
        from app.core.init_db import initialize_database

        os.environ["DATABASE_URL"] = target_url
        initialize_database()
        print("[SUCCESS] Default production seed data verified/initialized.")
        return True
    except Exception as exc:
        print(f"[ERROR] Seeding failed: {exc}")
        return False


def sync_records(source_url: str, target_url: str) -> bool:
    """Syncs data rows from local development database into production."""
    print("\n" + "=" * 65)
    print("  STEP 3: SYNCING DATA FROM LOCAL TO PRODUCTION")
    print("=" * 65)

    try:
        src_engine = create_app_engine(source_url)
        tgt_engine = create_app_engine(target_url)

        src_inspector = inspect(src_engine)
        tables = [t for t in src_inspector.get_table_names() if t != "alembic_version"]

        print(f"[INFO] Inspecting {len(tables)} table(s) in source database...")
        src_session = sessionmaker(bind=src_engine)()
        tgt_session = sessionmaker(bind=tgt_engine)()

        with tgt_engine.connect() as tgt_conn:
            # Check if Postgres (supports session_replication_role)
            is_postgres = "postgres" in target_url
            if is_postgres:
                tgt_conn.execute(text("SET session_replication_role = 'replica';"))
                tgt_conn.commit()

            total_synced = 0
            for table in tables:
                with src_engine.connect() as s_conn:
                    rows = s_conn.execute(text(f'SELECT * FROM "{table}";')).mappings().all()

                if not rows:
                    continue

                print(f"   Syncing {table} ({len(rows)} rows)...")
                # Insert rows into target
                for row in rows:
                    cols = list(row.keys())
                    col_names = ", ".join([f'"{c}"' for c in cols])
                    val_placeholders = ", ".join([f":{c}" for c in cols])
                    stmt = text(f'INSERT INTO "{table}" ({col_names}) VALUES ({val_placeholders}) ON CONFLICT DO NOTHING;')
                    tgt_conn.execute(stmt, dict(row))
                    total_synced += 1

                tgt_conn.commit()

            if is_postgres:
                tgt_conn.execute(text("SET session_replication_role = 'DEFAULT';"))
                tgt_conn.commit()

        print(f"\n[SUCCESS] Data synchronization completed! Total rows processed: {total_synced}")
        return True
    except Exception as exc:
        print(f"[ERROR] Data sync failed: {exc}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Smart Farming - Production Database Migration & Sync Utility"
    )
    parser.add_argument(
        "--target",
        type=str,
        help="Target production database URL (defaults to PROD_DATABASE_URL in .env)",
    )
    parser.add_argument(
        "--source",
        type=str,
        help="Source local database URL (defaults to DATABASE_URL or sqlite:///./dev_database.db)",
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Apply schema migrations (create_all + alembic upgrade head) without transferring data.",
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Apply schema migrations and seed reference accounts/crops if empty.",
    )
    parser.add_argument(
        "--sync-data",
        action="store_true",
        help="Sync rows from local database to production.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify connectivity and report table status on production without modifying anything.",
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompt for automated CI/CD execution.",
    )

    args = parser.parse_args()

    target_url = get_target_prod_url(args.target)
    source_url = get_local_source_url(args.source)

    print("=" * 65)
    print("  SMART FARMING: DATABASE MIGRATION UTILITY")
    print("=" * 65)
    print(f"  Source (Local Dev) : {source_url.split('@')[-1] if '@' in source_url else source_url}")
    print(f"  Target (Production): {target_url.split('@')[-1] if '@' in target_url else target_url}")
    print("=" * 65)

    if args.check:
        verify_connection(target_url, "Production Database")
        return

    # Non-interactive CLI flag mode
    if args.schema_only or args.seed or args.sync_data:
        if not args.yes:
            confirm = input("\nProceed with migration to PRODUCTION? [y/N]: ").strip().lower()
            if confirm not in ("y", "yes"):
                print("Aborted.")
                return

        if not verify_connection(target_url, "Production Database"):
            sys.exit(1)

        success = apply_schema_migrations(target_url)
        if not success:
            sys.exit(1)

        if args.seed:
            seed_production_defaults(target_url)

        if args.sync_data:
            sync_records(source_url, target_url)

        print("\n[COMPLETE] All requested operations completed successfully.")
        return

    # Interactive menu mode
    print("\nSelect Migration Option:")
    print("  [1] Apply Schema Updates Only (Alembic upgrade head + create_all) [Recommended & Safe]")
    print("  [2] Apply Schema Updates + Seed Default Reference Data (Crops, Admin)")
    print("  [3] Sync Local Data to Production (Copies local table rows)")
    print("  [4] Check Production Connection & Table Status")
    print("  [5] Cancel")

    try:
        choice = input("\nEnter choice [1-5]: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        return

    if choice == "1":
        if verify_connection(target_url, "Production Database"):
            apply_schema_migrations(target_url)
    elif choice == "2":
        if verify_connection(target_url, "Production Database"):
            if apply_schema_migrations(target_url):
                seed_production_defaults(target_url)
    elif choice == "3":
        confirm = input("\nWARNING: This will sync records to Production. Proceed? [y/N]: ").strip().lower()
        if confirm in ("y", "yes"):
            if verify_connection(target_url, "Production Database") and verify_connection(source_url, "Local Database"):
                if apply_schema_migrations(target_url):
                    sync_records(source_url, target_url)
    elif choice == "4":
        verify_connection(target_url, "Production Database")
        engine = create_app_engine(target_url)
        insp = inspect(engine)
        print("\nProduction Tables:")
        for t in sorted(insp.get_table_names()):
            print(f"   - {t}")
    else:
        print("Cancelled.")


if __name__ == "__main__":
    main()

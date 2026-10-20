"""Shared utilities for backend maintenance and migration scripts.

Provides centralized database URL sanitization, environment configuration loading,
and safety guards against unintended production mutations.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure backend root and backend/src are in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(backend_dir / "src") not in sys.path:
    sys.path.insert(0, str(backend_dir / "src"))


def load_env_file(env_name: str = "dev") -> Path:
    """Load the appropriate .env file based on environment."""
    if env_name in ("prod", "production"):
        env_file = backend_dir / ".env.production"
        if not env_file.exists():
            env_file = backend_dir / ".env"
    else:
        env_file = backend_dir / ".env"

    if env_file.exists():
        load_dotenv(env_file, override=False)
    return env_file


def sanitize_db_url(url: str | None) -> str:
    """Normalize PostgreSQL connection string and strip quotes."""
    if not url:
        return ""
    clean = url.strip().strip("'").strip('"')
    if clean.startswith("postgres://"):
        clean = "postgresql://" + clean[len("postgres://"):]
    return clean


def confirm_prod_action(action_description: str, auto_confirm: bool = False) -> None:
    """Prompt for explicit developer confirmation before performing a destructive action on production."""
    if auto_confirm:
        return

    print("\n" + "!" * 65)
    print("  [CRITICAL WARNING] PRODUCTION TARGET DETECTED")
    print(f"  Action: {action_description}")
    print("!" * 65)

    try:
        response = input("Type 'CONFIRM' to proceed, or press Enter / Ctrl+C to abort: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n[ABORTED] Operation cancelled by user.")
        sys.exit(1)

    if response != "CONFIRM":
        print("\n[ABORTED] Confirmation failed. Operation cancelled.")
        sys.exit(1)


def get_supabase_env_config(env_name: str = "dev") -> dict[str, str]:
    """Retrieve Supabase URL, Service Key, and DB URL for the specified environment."""
    load_env_file(env_name)

    if env_name in ("prod", "production"):
        supabase_url = os.getenv("PROD_SUPABASE_URL") or os.getenv("SUPABASE_URL", "")
        service_key = (
            os.getenv("PROD_SUPABASE_SERVICE_ROLE_KEY")
            or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        )
        db_url = os.getenv("PROD_DATABASE_URL") or os.getenv("SUPABASE_DATABASE_URL", "")
        label = "Production (smart-farming)"
    else:
        supabase_url = os.getenv("DEV_SUPABASE_URL") or os.getenv("SUPABASE_URL", "")
        service_key = (
            os.getenv("DEV_SUPABASE_SERVICE_ROLE_KEY")
            or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        )
        db_url = os.getenv("DEV_DATABASE_URL") or os.getenv("DATABASE_URL", "")
        label = "Development (smart-farming-dev)"

    return {
        "label": label,
        "supabase_url": supabase_url.rstrip("/"),
        "service_role_key": service_key,
        "db_url": sanitize_db_url(db_url),
    }


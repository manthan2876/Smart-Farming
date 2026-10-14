from __future__ import annotations

import os
from typing import Any
from collections.abc import Generator
from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

def _find_env_file() -> Path | None:
    env_name = os.getenv("ENV_FILE") or (".env.production" if os.getenv("ENVIRONMENT") == "production" else ".env")
    candidates = [
        Path(__file__).resolve().parents[3] / env_name,  # backend/.env[.production]
        Path(__file__).resolve().parents[4] / env_name,  # project/.env[.production]
        Path.cwd() / env_name,
        Path.cwd() / "backend" / env_name,
        Path(__file__).resolve().parents[3] / ".env",
        Path.cwd() / ".env",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


env_file = _find_env_file()
if env_file:
    load_dotenv(env_file)
else:
    load_dotenv()


def sanitize_db_url(url: str | None) -> str:
    """Safely sanitize database URLs, auto-encoding special characters (like '@') in passwords and mapping postgres:// to postgresql://."""
    if not url:
        return "sqlite:///./dev_database.db"
    clean = url.strip().strip("'\"")
    if "://" not in clean:
        return clean
    scheme, remainder = clean.split("://", 1)
    if scheme == "postgres":
        scheme = "postgresql"
    if "@" not in remainder:
        return f"{scheme}://{remainder}"
    userinfo, _, hostinfo = remainder.rpartition("@")
    if ":" in userinfo:
        user, pwd = userinfo.split(":", 1)
        import urllib.parse
        clean_user = user.strip().strip("'\"")
        clean_pwd = pwd.strip().strip("'\"")
        if clean_pwd.startswith("[") and clean_pwd.endswith("]"):
            clean_pwd = clean_pwd[1:-1].strip()
        clean_pwd = urllib.parse.quote(urllib.parse.unquote(clean_pwd), safe="")
        clean_user = urllib.parse.quote(urllib.parse.unquote(clean_user), safe=".")
        return f"{scheme}://{clean_user}:{clean_pwd}@{hostinfo}"
    return f"{scheme}://{remainder}"


def database_url() -> str:
    raw = os.getenv(
        "DATABASE_URL",
        "sqlite:///./dev_database.db",
    )
    return sanitize_db_url(raw)


def get_db_connect_args(url: str) -> dict[str, Any]:
    """Return appropriate connect_args for the database engine.

    For SQLite: disables thread check.
    For PostgreSQL: resolves cloud hostnames (such as Supabase) with fallback to
    public DNS (8.8.8.8, 1.1.1.1) to prevent 'could not translate host name'
    errors caused by slow or misconfigured local network / Wi-Fi DNS.
    """
    if "sqlite" in url:
        return {"check_same_thread": False}

    connect_args: dict[str, Any] = {}
    if "postgresql" in url or "postgres" in url:
        connect_args.setdefault("keepalives", 1)
        connect_args.setdefault("keepalives_idle", 30)
        connect_args.setdefault("keepalives_interval", 10)
        connect_args.setdefault("keepalives_count", 5)

        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            if hostname and hostname not in ("localhost", "127.0.0.1", "0.0.0.0") and "hostaddr=" not in url:
                import socket
                try:
                    socket.gethostbyname(hostname)
                except Exception:
                    # Only fallback to manual DNS resolver if local system DNS resolution fails
                    try:
                        import dns.resolver
                        resolver = dns.resolver.Resolver()
                        resolver.nameservers = ["8.8.8.8", "1.1.1.1", "8.8.4.4"]
                        resolver.timeout = 3.0
                        resolver.lifetime = 3.0
                        answers = resolver.resolve(hostname, "A")
                        for r in answers:
                            connect_args["hostaddr"] = r.to_text()
                            break
                    except Exception:
                        pass
        except Exception:
            pass

    return connect_args


def create_app_engine(url: str | None = None, **kwargs):
    target_url = sanitize_db_url(url or database_url())
    # Normalize postgresql:// to postgresql+psycopg2:// or postgresql+psycopg:// depending on installed driver
    if target_url.startswith("postgresql://"):
        try:
            import psycopg2  # type: ignore
            target_url = target_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        except ImportError:
            try:
                import psycopg  # type: ignore
                target_url = target_url.replace("postgresql://", "postgresql+psycopg://", 1)
            except ImportError:
                target_url = target_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    connect_args = get_db_connect_args(target_url)
    if "connect_args" in kwargs:
        connect_args.update(kwargs.pop("connect_args"))

    if target_url.startswith("sqlite"):
        return create_engine(target_url, connect_args=connect_args, **kwargs)

    # For PostgreSQL via Supabase Pooler (Supavisor / PgBouncer), disable prepare_threshold for psycopg (psycopg3)
    if "postgresql+psycopg://" in target_url and "prepare_threshold" not in connect_args:
        connect_args["prepare_threshold"] = 0

    engine_kwargs = {
        "connect_args": connect_args,
    }
    from sqlalchemy.pool import NullPool
    if kwargs.get("poolclass") is not NullPool:
        engine_kwargs.update({
            "pool_size": 5,
            "max_overflow": 5,
            "pool_recycle": 60,  # Recycle connections after 60s to prevent stale cloud pooler drops
            "pool_pre_ping": True,
        })
    engine_kwargs.update(kwargs)
    return create_engine(target_url, **engine_kwargs)


@lru_cache(maxsize=1)
def _session_factory() -> sessionmaker[Session]:
    engine = create_app_engine()
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)



def get_session() -> Generator[Session, None, None]:
    session = _session_factory()()
    try:
        yield session
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    finally:
        session.close()

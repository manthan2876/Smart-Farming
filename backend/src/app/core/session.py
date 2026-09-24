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
    candidates = [
        Path(__file__).resolve().parents[3] / ".env",  # backend/.env
        Path(__file__).resolve().parents[4] / ".env",  # project/.env
        Path.cwd() / ".env",
        Path.cwd() / "backend" / ".env",
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


def database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "sqlite:///./dev_database.db",
    )


def get_db_connect_args(url: str) -> dict[str, Any]:
    """Return appropriate connect_args for the database engine.

    For SQLite: disables thread check.
    For PostgreSQL: resolves cloud hostnames (such as Render) with fallback to
    public DNS (8.8.8.8, 1.1.1.1) to prevent 'could not translate host name'
    errors caused by slow or misconfigured local network / Wi-Fi DNS.
    """
    if "sqlite" in url:
        return {"check_same_thread": False}

    connect_args: dict[str, Any] = {}
    if "postgresql" in url or "postgres" in url:
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            if hostname and hostname not in ("localhost", "127.0.0.1", "0.0.0.0") and "hostaddr=" not in url:
                import socket
                resolved_ip: str | None = None
                try:
                    resolved_ip = socket.gethostbyname(hostname)
                except Exception:
                    try:
                        import dns.resolver
                        resolver = dns.resolver.Resolver()
                        resolver.nameservers = ["8.8.8.8", "1.1.1.1", "8.8.4.4"]
                        resolver.timeout = 3.0
                        resolver.lifetime = 3.0
                        answers = resolver.resolve(hostname, "A")
                        for r in answers:
                            resolved_ip = r.to_text()
                            break
                    except Exception:
                        if "singapore-postgres.render.com" in hostname:
                            resolved_ip = "18.142.152.125"

                if resolved_ip:
                    connect_args["hostaddr"] = resolved_ip
        except Exception:
            pass

    return connect_args


def create_app_engine(url: str | None = None):
    target_url = url or database_url()
    connect_args = get_db_connect_args(target_url)
    if target_url.startswith("sqlite"):
        return create_engine(target_url, connect_args=connect_args)
    return create_engine(
        target_url,
        pool_size=15,
        max_overflow=20,
        pool_recycle=1200,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


@lru_cache(maxsize=1)
def _session_factory() -> sessionmaker[Session]:
    engine = create_app_engine()
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)



def get_session() -> Generator[Session, None, None]:
    try:
        session = _session_factory()()
        session.connection()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    try:
        yield session
    finally:
        session.close()

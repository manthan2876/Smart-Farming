from __future__ import annotations

import os
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


@lru_cache(maxsize=1)
def _session_factory() -> sessionmaker[Session]:
    url = database_url()
    if url.startswith("sqlite"):
        engine = create_engine(url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(
            url, pool_size=3, max_overflow=0, pool_recycle=1200, pool_pre_ping=True
        )
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

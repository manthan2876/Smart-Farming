from __future__ import annotations

import os
from collections.abc import Generator
from functools import lru_cache

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker


def database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres@localhost:5432/smart_farming",
    )


@lru_cache(maxsize=1)
def _session_factory() -> sessionmaker[Session]:
    engine = create_engine(database_url(), pool_pre_ping=True)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session() -> Generator[Session, None, None]:
    try:
        session = _session_factory()()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    try:
        yield session
    finally:
        session.close()

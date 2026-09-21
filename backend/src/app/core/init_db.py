from __future__ import annotations

from sqlalchemy import create_engine, inspect, text

from app.core import Base, database_url
from app.core.config import settings
import app.models

def initialize_database() -> None:
    url = database_url()
    if url.startswith("sqlite"):
        engine = create_engine(url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(
            url, pool_size=15, max_overflow=20, pool_recycle=1200, pool_pre_ping=True
        )
    Base.metadata.create_all(engine)
    try:
        with engine.begin() as connection:
            existing_columns = {column["name"] for column in inspect(engine).get_columns("farms")}
            if "boundary" not in existing_columns:
                connection.execute(text("ALTER TABLE farms ADD COLUMN boundary JSON"))
            if not url.startswith("sqlite"):
                connection.execute(
                    text("ALTER TABLE farms ADD COLUMN IF NOT EXISTS name VARCHAR(200)")
                )
                connection.execute(
                    text("ALTER TABLE farms ADD COLUMN IF NOT EXISTS area_acres FLOAT")
                )
                connection.execute(
                    text("ALTER TABLE predictions ADD COLUMN IF NOT EXISTS plot_id INTEGER")
                )
                connection.execute(
                    text("ALTER TABLE predictions ADD COLUMN IF NOT EXISTS crop_conf FLOAT")
                )
                connection.execute(
                    text("ALTER TABLE predictions ADD COLUMN IF NOT EXISTS disease_conf FLOAT")
                )
                connection.execute(
                    text("ALTER TABLE predictions ADD COLUMN IF NOT EXISTS model_used VARCHAR(200)")
                )
                connection.execute(
                    text("ALTER TABLE predictions ADD COLUMN IF NOT EXISTS severity_pct FLOAT")
                )
                connection.execute(
                    text("ALTER TABLE predictions ADD COLUMN IF NOT EXISTS parent_id INTEGER REFERENCES predictions(id)")
                )
    except Exception as exc:
        print(f"[InitDB] Note on migrations: {exc}")
    try:
        from alembic import command
        from alembic.config import Config

        alembic_config = Config(str(settings.BACKEND_ROOT / "alembic.ini"))
        command.upgrade(alembic_config, "head")
    except Exception as exc:
        print(f"[InitDB] Alembic migration note: {exc}")
    print("Smart Farming database tables are ready.")



if __name__ == "__main__":
    initialize_database()

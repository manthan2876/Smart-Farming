from __future__ import annotations

from sqlalchemy import create_engine, text

try:
    from backend.database.models import Base
    from backend.database.session import database_url
except ModuleNotFoundError:
    from database.models import Base
    from database.session import database_url


def initialize_database() -> None:
    engine = create_engine(database_url(), pool_size=3, max_overflow=0, pool_recycle=1200, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            text("ALTER TABLE farms ADD COLUMN IF NOT EXISTS name VARCHAR(200)")
        )
        connection.execute(
            text("ALTER TABLE farms ADD COLUMN IF NOT EXISTS area_acres FLOAT")
        )
        # Add missing prediction columns
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
    print("Smart Farming database tables are ready.")


if __name__ == "__main__":
    initialize_database()

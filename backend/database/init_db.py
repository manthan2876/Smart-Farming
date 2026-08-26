from __future__ import annotations

from sqlalchemy import create_engine, text

try:
    from backend.database.models import Base
    from backend.database.session import database_url
except ModuleNotFoundError:
    from database.models import Base
    from database.session import database_url


def initialize_database() -> None:
    engine = create_engine(database_url())
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        # create_all does not add columns to an existing local database.
        connection.execute(
            text("ALTER TABLE farms ADD COLUMN IF NOT EXISTS name VARCHAR(200)")
        )
        connection.execute(
            text("ALTER TABLE farms ADD COLUMN IF NOT EXISTS area_acres FLOAT")
        )
    print("Smart Farming database tables are ready.")


if __name__ == "__main__":
    initialize_database()

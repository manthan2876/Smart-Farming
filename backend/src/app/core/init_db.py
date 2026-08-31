from __future__ import annotations

from sqlalchemy import create_engine, text

from app.core import Base, database_url

def initialize_database() -> None:
    url = database_url()
    if url.startswith("sqlite"):
        engine = create_engine(url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(
            url, pool_size=3, max_overflow=0, pool_recycle=1200, pool_pre_ping=True
        )
    Base.metadata.create_all(engine)
    if not url.startswith("sqlite"):
        try:
            with engine.begin() as connection:
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
        except Exception as exc:
            print(f"[InitDB] Note on migrations: {exc}")
    print("Smart Farming database tables are ready.")



if __name__ == "__main__":
    initialize_database()

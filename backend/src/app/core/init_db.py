from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from app.core import Base, database_url
from app.core.session import create_app_engine
from app.core.config import settings
import app.models

logger = logging.getLogger("smart-farming.init_db")


def _ensure_column(
    connection,
    inspector,
    table_name: str,
    column_name: str,
    column_type_sql: str,
    is_sqlite: bool,
) -> None:
    """Ensure a column exists on an existing table across PostgreSQL and SQLite."""
    if not inspector.has_table(table_name):
        return
    existing_cols = {col["name"] for col in inspector.get_columns(table_name)}
    if column_name not in existing_cols:
        try:
            if is_sqlite:
                connection.execute(
                    text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type_sql}")
                )
            else:
                connection.execute(
                    text(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {column_type_sql}")
                )
            logger.info("Added missing column: %s.%s", table_name, column_name)
        except Exception as exc:
            logger.warning("Could not add column %s.%s: %s", table_name, column_name, exc)


def initialize_database() -> None:
    """
    Initialize database schema, apply missing column migrations,
    and seed default accounts if database is empty.
    """
    url = database_url()
    is_sqlite = url.startswith("sqlite")
    engine = create_app_engine(url)

    # 1. Create all metadata tables if they do not exist (with retry for cloud DB connections)
    import time
    for attempt in range(1, 4):
        try:
            Base.metadata.create_all(engine)
            break
        except Exception as exc:
            if attempt == 3:
                logger.error("Failed to connect to database after 3 attempts: %s", exc)
                raise
            logger.warning("Database connection attempt %d failed (%s). Retrying in %ds...", attempt, exc, attempt * 2)
            time.sleep(attempt * 2)

    # 2. Apply inline column additions for existing production / development databases
    try:
        with engine.begin() as connection:
            inspector = inspect(engine)
            ts_type = "DATETIME" if is_sqlite else "TIMESTAMP WITH TIME ZONE"
            json_type = "JSON" if is_sqlite else "JSON"

            # Users table
            _ensure_column(connection, inspector, "users", "deleted_at", ts_type, is_sqlite)
            _ensure_column(connection, inspector, "users", "role", "VARCHAR(32)", is_sqlite)
            _ensure_column(connection, inspector, "users", "language", "VARCHAR(32)", is_sqlite)

            # Farms table
            _ensure_column(connection, inspector, "farms", "boundary", json_type, is_sqlite)
            _ensure_column(connection, inspector, "farms", "name", "VARCHAR(200)", is_sqlite)
            _ensure_column(connection, inspector, "farms", "area_acres", "FLOAT", is_sqlite)
            _ensure_column(connection, inspector, "farms", "latitude", "FLOAT", is_sqlite)
            _ensure_column(connection, inspector, "farms", "longitude", "FLOAT", is_sqlite)

            # Plots table
            _ensure_column(connection, inspector, "plots", "geometry", json_type, is_sqlite)
            _ensure_column(connection, inspector, "plots", "status", "VARCHAR(50)", is_sqlite)
            _ensure_column(connection, inspector, "plots", "crop", "VARCHAR(100)", is_sqlite)
            _ensure_column(connection, inspector, "plots", "area_acres", "FLOAT", is_sqlite)

            # Predictions table
            _ensure_column(connection, inspector, "predictions", "plot_id", "INTEGER", is_sqlite)
            _ensure_column(connection, inspector, "predictions", "crop_conf", "FLOAT", is_sqlite)
            _ensure_column(connection, inspector, "predictions", "disease_conf", "FLOAT", is_sqlite)
            _ensure_column(connection, inspector, "predictions", "model_used", "VARCHAR(200)", is_sqlite)
            _ensure_column(connection, inspector, "predictions", "severity_pct", "FLOAT", is_sqlite)
            _ensure_column(connection, inspector, "predictions", "status", "VARCHAR(50)", is_sqlite)
            _ensure_column(connection, inspector, "predictions", "parent_id", "INTEGER", is_sqlite)
            _ensure_column(connection, inspector, "predictions", "raw_path", "VARCHAR(500)", is_sqlite)
            _ensure_column(connection, inspector, "predictions", "processed_path", "VARCHAR(500)", is_sqlite)

            # Dataset candidates
            _ensure_column(connection, inspector, "dataset_candidates", "provenance_note", "TEXT", is_sqlite)
            _ensure_column(connection, inspector, "dataset_candidates", "source_feedback_id", "INTEGER", is_sqlite)

            # Feedback
            _ensure_column(connection, inspector, "feedback", "corrected_label", "VARCHAR(200)", is_sqlite)
            _ensure_column(connection, inspector, "feedback", "review_status", "VARCHAR(50)", is_sqlite)
            _ensure_column(connection, inspector, "feedback", "review_decision", "VARCHAR(50)", is_sqlite)
            _ensure_column(connection, inspector, "feedback", "reviewer_id", "VARCHAR(128)", is_sqlite)
            _ensure_column(connection, inspector, "feedback", "reviewer_note", "TEXT", is_sqlite)
            _ensure_column(connection, inspector, "feedback", "reviewed_at", ts_type, is_sqlite)

            # Expert reviews
            _ensure_column(connection, inspector, "expert_reviews", "corrected_disease", "VARCHAR(200)", is_sqlite)
            _ensure_column(connection, inspector, "expert_reviews", "corrected_severity", "VARCHAR(50)", is_sqlite)
            _ensure_column(connection, inspector, "expert_reviews", "farmer_guidance", "TEXT", is_sqlite)
            _ensure_column(connection, inspector, "expert_reviews", "internal_note", "TEXT", is_sqlite)

            # MLOps runs
            _ensure_column(connection, inspector, "mlops_runs", "dataset_export_config", json_type, is_sqlite)
            _ensure_column(connection, inspector, "mlops_runs", "metrics", json_type, is_sqlite)

    except Exception as exc:
        print(f"[InitDB] Note on schema migrations: {exc}")

    # 3. Seed initial users if database is empty
    try:
        from app.models.user import User
        from app.models.farm import Farm
        from app.api.deps import hash_password

        with Session(engine) as session:
            user_count = session.query(User).count()
            if user_count == 0:
                print("[InitDB] Database is empty. Seeding initial platform accounts...")

                admin_user = User(
                    id=str(uuid.uuid4()),
                    name="Admin User",
                    email="admin@smartfarming.com",
                    phone="+10000000001",
                    role="admin",
                    language="English",
                    password_hash=hash_password("admin123"),
                    created_at=datetime.now(timezone.utc),
                )
                session.add(admin_user)

                expert_user = User(
                    id=str(uuid.uuid4()),
                    name="Expert Agronomist",
                    email="expert@smartfarming.com",
                    phone="+10000000002",
                    role="expert",
                    language="English",
                    password_hash=hash_password("expert123"),
                    created_at=datetime.now(timezone.utc),
                )
                session.add(expert_user)

                farmer_user = User(
                    id=str(uuid.uuid4()),
                    name="Farmer John",
                    email="farmer@smartfarming.com",
                    phone="+10000000003",
                    role="farmer",
                    language="English",
                    password_hash=hash_password("farmer123"),
                    created_at=datetime.now(timezone.utc),
                )
                session.add(farmer_user)
                session.flush()

                # Seed sample farm for the farmer
                sample_farm = Farm(
                    user_id=farmer_user.id,
                    name="Green Valley Farms",
                    location="Bhavnagar, Gujarat",
                    area_acres=25.0,
                    latitude=21.7645,
                    longitude=72.1519,
                    crop_history=["Tomato", "Cotton"],
                )
                session.add(sample_farm)
                session.commit()
                print("[InitDB] Seeded initial accounts: admin@smartfarming.com, expert@smartfarming.com, farmer@smartfarming.com (password: admin123 / expert123 / farmer123)")
    except Exception as exc:
        print(f"[InitDB] Note on user seeding: {exc}")

    # 4. Run Alembic upgrade if configured
    try:
        from alembic import command
        from alembic.config import Config

        alembic_ini_path = settings.BACKEND_ROOT / "alembic.ini"
        if alembic_ini_path.exists():
            alembic_config = Config(str(alembic_ini_path))
            alembic_config.set_main_option("script_location", str(settings.BACKEND_ROOT / "alembic"))
            command.upgrade(alembic_config, "head")
    except Exception as exc:
        print(f"[InitDB] Alembic migration note: {exc}")

    print("Smart Farming database tables and columns are ready.")


if __name__ == "__main__":
    initialize_database()

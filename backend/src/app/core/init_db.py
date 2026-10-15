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
    cols_cache: dict[str, set[str]] | None = None,
) -> None:
    """Ensure a column exists on an existing table across PostgreSQL and SQLite."""
    if cols_cache is not None:
        if table_name not in cols_cache:
            if not inspector.has_table(table_name):
                cols_cache[table_name] = set()
            else:
                cols_cache[table_name] = {col["name"] for col in inspector.get_columns(table_name)}
        existing_cols = cols_cache[table_name]
    else:
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
            existing_cols.add(column_name)
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
            inspector = inspect(connection)
            cols_cache: dict[str, set[str]] = {}
            ts_type = "DATETIME" if is_sqlite else "TIMESTAMP WITH TIME ZONE"
            json_type = "JSON" if is_sqlite else "JSON"

            # Users table
            _ensure_column(connection, inspector, "users", "deleted_at", ts_type, is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "users", "role", "VARCHAR(32)", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "users", "language", "VARCHAR(32)", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "users", "is_email_verified", "BOOLEAN DEFAULT FALSE", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "users", "pending_email", "VARCHAR(320)", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "users", "email_verified_at", ts_type, is_sqlite, cols_cache)

            # Auto-verify existing legacy seeded accounts that already had email & password
            try:
                if is_sqlite:
                    connection.execute(
                        text("UPDATE users SET is_email_verified = 1 WHERE email IS NOT NULL AND password_hash IS NOT NULL AND (is_email_verified IS NULL OR is_email_verified = 0)")
                    )
                else:
                    connection.execute(
                        text("UPDATE users SET is_email_verified = TRUE WHERE email IS NOT NULL AND password_hash IS NOT NULL AND (is_email_verified IS NULL OR is_email_verified IS NOT TRUE)")
                    )
            except Exception:
                pass

            # Farms table
            _ensure_column(connection, inspector, "farms", "boundary", json_type, is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "farms", "name", "VARCHAR(200)", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "farms", "area_acres", "FLOAT", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "farms", "latitude", "FLOAT", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "farms", "longitude", "FLOAT", is_sqlite, cols_cache)

            # Plots table
            _ensure_column(connection, inspector, "plots", "geometry", json_type, is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "plots", "status", "VARCHAR(50)", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "plots", "crop", "VARCHAR(100)", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "plots", "area_acres", "FLOAT", is_sqlite, cols_cache)

            # Predictions table
            _ensure_column(connection, inspector, "predictions", "plot_id", "INTEGER", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "predictions", "crop_conf", "FLOAT", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "predictions", "disease_conf", "FLOAT", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "predictions", "model_used", "VARCHAR(200)", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "predictions", "severity_pct", "FLOAT", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "predictions", "status", "VARCHAR(50)", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "predictions", "parent_id", "INTEGER", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "predictions", "raw_path", "VARCHAR(500)", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "predictions", "processed_path", "VARCHAR(500)", is_sqlite, cols_cache)

            # Dataset candidates
            _ensure_column(connection, inspector, "dataset_candidates", "provenance_note", "TEXT", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "dataset_candidates", "source_feedback_id", "INTEGER", is_sqlite, cols_cache)

            # Feedback
            _ensure_column(connection, inspector, "feedback", "corrected_label", "VARCHAR(200)", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "feedback", "review_status", "VARCHAR(50)", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "feedback", "review_decision", "VARCHAR(50)", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "feedback", "reviewer_id", "VARCHAR(128)", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "feedback", "reviewer_note", "TEXT", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "feedback", "reviewed_at", ts_type, is_sqlite, cols_cache)

            # Expert reviews
            _ensure_column(connection, inspector, "expert_reviews", "corrected_disease", "VARCHAR(200)", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "expert_reviews", "corrected_severity", "VARCHAR(50)", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "expert_reviews", "farmer_guidance", "TEXT", is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "expert_reviews", "internal_note", "TEXT", is_sqlite, cols_cache)

            # MLOps runs
            _ensure_column(connection, inspector, "mlops_runs", "dataset_export_config", json_type, is_sqlite, cols_cache)
            _ensure_column(connection, inspector, "mlops_runs", "metrics", json_type, is_sqlite, cols_cache)

            if not is_sqlite:
                # Ensure foreign key constraints on user-referencing tables use CASCADE / SET NULL
                fkey_updates = [
                    ("farms", "farms_user_id_fkey", "user_id", "users(id)", "CASCADE"),
                    ("plots", "plots_farm_id_fkey", "farm_id", "farms(id)", "CASCADE"),
                    ("images", "images_user_id_fkey", "user_id", "users(id)", "CASCADE"),
                    ("predictions", "predictions_user_id_fkey", "user_id", "users(id)", "CASCADE"),
                    ("alerts", "alerts_user_id_fkey", "user_id", "users(id)", "CASCADE"),
                    ("password_reset_tokens", "password_reset_tokens_user_id_fkey", "user_id", "users(id)", "CASCADE"),
                    ("email_verification_tokens", "email_verification_tokens_user_id_fkey", "user_id", "users(id)", "CASCADE"),
                    ("expert_reviews", "expert_reviews_expert_id_fkey", "expert_id", "users(id)", "SET NULL"),
                    ("feedback", "feedback_reviewer_id_fkey", "reviewer_id", "users(id)", "SET NULL"),
                ]
                for tbl, cname, col, target, action in fkey_updates:
                    try:
                        connection.execute(text(f"""
                            DO $$
                            BEGIN
                                IF EXISTS (
                                    SELECT 1 FROM information_schema.tables WHERE table_name = '{tbl}'
                                ) THEN
                                    IF NOT EXISTS (
                                        SELECT 1 FROM information_schema.referential_constraints rc
                                        JOIN information_schema.table_constraints tc ON rc.constraint_name = tc.constraint_name
                                        WHERE tc.table_name = '{tbl}' AND tc.constraint_name = '{cname}' AND rc.delete_rule = '{action}' AND rc.update_rule = 'CASCADE'
                                    ) THEN
                                        EXECUTE 'ALTER TABLE {tbl} DROP CONSTRAINT IF EXISTS {cname}';
                                        EXECUTE 'ALTER TABLE {tbl} ADD CONSTRAINT {cname} FOREIGN KEY ({col}) REFERENCES {target} ON DELETE {action} ON UPDATE CASCADE';
                                    END IF;
                                END IF;
                            END $$;
                        """))
                    except Exception as fkey_err:
                        logger.debug("Constraint update note for %s.%s: %s", tbl, cname, fkey_err)

                # Ensure handle_new_user trigger function handles existing email accounts without duplicate key errors
                try:
                    connection.execute(text("""
                        CREATE OR REPLACE FUNCTION handle_new_user()
                        RETURNS trigger
                        LANGUAGE plpgsql
                        SECURITY DEFINER
                        AS $func$
                        DECLARE
                          v_role text;
                          v_name text;
                          v_language text;
                          v_farm_name text;
                          v_location text;
                          v_existing_id text;
                        BEGIN
                          v_role := coalesce(new.raw_user_meta_data->>'role', 'farmer');
                          v_name := coalesce(new.raw_user_meta_data->>'name', split_part(new.email, '@', 1));
                          v_language := coalesce(new.raw_user_meta_data->>'language', 'English');
                          v_location := coalesce(new.raw_user_meta_data->>'location', 'Gujarat, India');
                          v_farm_name := coalesce(new.raw_user_meta_data->>'farm_name', concat(v_name, '''s Farm'));

                          IF new.id IS NOT NULL THEN
                            SELECT id INTO v_existing_id FROM public.users WHERE id = new.id::text;
                          END IF;
                          
                          IF v_existing_id IS NULL AND new.email IS NOT NULL THEN
                            SELECT id INTO v_existing_id FROM public.users WHERE lower(email) = lower(new.email);
                          END IF;

                          IF v_existing_id IS NOT NULL THEN
                            UPDATE public.users SET
                              id = new.id::text,
                              email = coalesce(new.email, public.users.email),
                              phone = coalesce(new.phone, public.users.phone),
                              name = coalesce(v_name, public.users.name),
                              role = coalesce(v_role, public.users.role),
                              language = coalesce(v_language, public.users.language)
                            WHERE id = v_existing_id;
                          ELSE
                            INSERT INTO public.users (
                              id,
                              email,
                              phone,
                              name,
                              language,
                              role,
                              created_at
                            )
                            VALUES (
                              new.id::text,
                              new.email,
                              new.phone,
                              v_name,
                              v_language,
                              v_role,
                              coalesce(new.created_at, now())
                            )
                            ON CONFLICT (id) DO UPDATE SET
                              email = excluded.email,
                              phone = coalesce(excluded.phone, public.users.phone),
                              name = coalesce(excluded.name, public.users.name),
                              role = coalesce(excluded.role, public.users.role);
                          END IF;

                          IF v_role = 'farmer' THEN
                            INSERT INTO public.farms (
                              user_id,
                              name,
                              location,
                              area_acres,
                              latitude,
                              longitude,
                              crop_history
                            )
                            VALUES (
                              new.id::text,
                              v_farm_name,
                              v_location,
                              nullif(new.raw_user_meta_data->>'farm_area_acres', '')::double precision,
                              nullif(new.raw_user_meta_data->>'latitude', '')::double precision,
                              nullif(new.raw_user_meta_data->>'longitude', '')::double precision,
                              '[]'::json
                            )
                            ON CONFLICT (user_id) DO NOTHING;
                          END IF;

                          RETURN new;
                        END;
                        $func$;
                    """))
                except Exception as trigger_err:
                    logger.debug("Trigger update note: %s", trigger_err)

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
                    is_email_verified=True,
                    email_verified_at=datetime.now(timezone.utc),
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
                    is_email_verified=True,
                    email_verified_at=datetime.now(timezone.utc),
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
                    is_email_verified=True,
                    email_verified_at=datetime.now(timezone.utc),
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

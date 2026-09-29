import os
import sys
from pathlib import Path
from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "src"))

load_dotenv(backend_dir / ".env")

from sqlalchemy import text
from app.core.session import create_app_engine, sanitize_db_url

def reset_db_sequences(db_url: str, label: str = "Database"):
    print(f"\n[INFO] Checking and resetting sequences for: {label}...")
    engine = create_app_engine(db_url)
    with engine.connect() as conn:
        cols = conn.execute(text("""
            SELECT c.table_name, c.column_name
            FROM information_schema.columns c
            JOIN information_schema.tables t ON c.table_name = t.table_name
            WHERE t.table_schema = 'public' 
              AND t.table_type = 'BASE TABLE'
              AND (c.column_default LIKE 'nextval(%' OR c.identity_generation IS NOT NULL)
        """)).fetchall()

        updated = 0
        for table_name, column_name in cols:
            seq_name = conn.execute(
                text("SELECT pg_get_serial_sequence(:t, :c)"),
                {"t": f'public."{table_name}"', "c": column_name}
            ).scalar()
            
            if not seq_name:
                seq_name = conn.execute(
                    text("SELECT pg_get_serial_sequence(:t, :c)"),
                    {"t": table_name, "c": column_name}
                ).scalar()

            if seq_name:
                max_id = conn.execute(text(f'SELECT MAX("{column_name}") FROM "{table_name}"')).scalar()
                if max_id is not None and max_id > 0:
                    conn.execute(
                        text("SELECT setval(:seq, :max_id, true)"),
                        {"seq": seq_name, "max_id": max_id}
                    )
                    print(f"   - {table_name}.{column_name}: sequence '{seq_name}' updated to {max_id}")
                else:
                    conn.execute(
                        text("SELECT setval(:seq, 1, false)"),
                        {"seq": seq_name}
                    )
                    print(f"   - {table_name}.{column_name}: sequence '{seq_name}' initialized to 1 (empty)")
                updated += 1
        conn.commit()
    print(f"[SUCCESS] {updated} sequence(s) updated for {label}.\n")

if __name__ == "__main__":
    dev_url = os.getenv("DATABASE_URL")
    if dev_url:
        reset_db_sequences(dev_url, "Development (Aiven)")
    else:
        print("[ERROR] DATABASE_URL not set.")

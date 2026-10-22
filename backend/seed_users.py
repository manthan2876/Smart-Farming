import os
import sys
import uuid
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_ROOT / "src"))

from app.api.deps import hash_password
from app.core.database import SessionLocal
from app.models.farm import Farm
from app.models.user import User

SEED_USERS = (
    ("admin@smartfarming.com", "Admin User", "admin", "SEED_ADMIN_PASSWORD", "+10000000001"),
    ("expert@smartfarming.com", "Expert Agronomist", "expert", "SEED_EXPERT_PASSWORD", "+10000000002"),
    ("farmer@smartfarming.com", "Farmer John", "farmer", "SEED_FARMER_PASSWORD", "+10000000003"),
)


def seed_users() -> None:
    passwords = {env_key: os.getenv(env_key, "") for _, _, _, env_key, _ in SEED_USERS}
    missing = [key for key, value in passwords.items() if not value]
    if missing:
        raise RuntimeError(f"Set these environment variables before seeding: {', '.join(missing)}")

    session = SessionLocal()
    try:
        for email, name, role, env_key, phone in SEED_USERS:
            if session.query(User).filter(User.email == email).first():
                print(f"User {email} already exists; leaving it unchanged.")
                continue

            user_id = str(uuid.uuid4())
            session.add(
                User(
                    id=user_id,
                    name=name,
                    email=email,
                    phone=phone,
                    password_hash=hash_password(passwords[env_key]),
                    role=role,
                    language="English",
                    is_email_verified=True,
                )
            )
            session.add(
                Farm(
                    user_id=user_id,
                    location="Test Farm Location",
                    latitude=0.0,
                    longitude=0.0,
                    crop_history=["Tomato", "Potato"],
                    name=f"{name}'s Farm",
                    area_acres=10.0,
                )
            )

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_users()
    print("Seeding completed successfully.")

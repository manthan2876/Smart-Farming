import sys
import os
from pathlib import Path
import uuid

# Add backend/src to path
sys.path.append(str(Path("src").resolve()))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.user import User
from app.models.farm import Farm
from app.api.deps import hash_password

def seed_users():
    session = SessionLocal()
    try:
        users = [
            {
                "email": "admin@smartfarming.com",
                "name": "Admin User",
                "role": "admin",
                "password": "password123",
                "phone": "+10000000001"
            },
            {
                "email": "expert@smartfarming.com",
                "name": "Expert Agronomist",
                "role": "expert",
                "password": "password123",
                "phone": "+10000000002"
            },
            {
                "email": "farmer@smartfarming.com",
                "name": "Farmer John",
                "role": "farmer",
                "password": "password123",
                "phone": "+10000000003"
            }
        ]

        for u in users:
            existing = session.query(User).filter(User.email == u["email"]).first()
            if existing:
                print(f"User {u['email']} already exists. Updating role...")
                existing.role = u["role"]
                existing.password_hash = hash_password(u["password"])
                existing.name = u["name"]
            else:
                print(f"Creating user {u['email']}...")
                user_id = str(uuid.uuid4())
                new_user = User(
                    id=user_id,
                    name=u["name"],
                    email=u["email"],
                    phone=u["phone"],
                    password_hash=hash_password(u["password"]),
                    role=u["role"],
                    language="English"
                )
                
                # Add a dummy farm so profile doesn't crash if farm is expected
                dummy_farm = Farm(
                    user_id=user_id,
                    location="Test Farm Location",
                    latitude=0.0,
                    longitude=0.0,
                    crop_history=["Tomato", "Potato"],
                    name=f"{u['name']}'s Farm",
                    area_acres=10.0
                )
                session.add(new_user)
                session.add(dummy_farm)
                
        session.commit()
        print("Seeding completed successfully.")

    except Exception as e:
        print(f"Error seeding users: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    seed_users()

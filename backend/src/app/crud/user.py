from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, select

from app.models import (
    Farm,
    User,
)

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email.ilike(email.strip())).first()


def create_user(
    session: Session,
    *,
    user_id: str,
    name: str,
    phone: str | None = None,
    email: str | None = None,
    password_hash: str | None = None,
    language: str = "English",
    location: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    crop_history: list[str] | None = None,
    farm_name: str | None = None,
    farm_area_acres: float | None = None,
    is_email_verified: bool = False,
    pending_email: str | None = None,
    email_verified_at: datetime | None = None,
) -> User:
    user = User(
        id=user_id,
        name=name,
        phone=phone,
        email=email,
        is_email_verified=is_email_verified,
        pending_email=pending_email,
        email_verified_at=email_verified_at,
        password_hash=password_hash,
        language=language,
    )
    user.farm = Farm(
        name=farm_name or (f"{name}'s Farm" if name else "My Farm"),
        location=location or "Gujarat, India",
        area_acres=farm_area_acres,
        latitude=latitude,
        longitude=longitude,
        crop_history=crop_history or [],
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def update_profile(
    session: Session,
    user: User,
    *,
    name: str | None,
    language: str | None,
    location: str | None,
    latitude: float | None,
    longitude: float | None,
    crop_history: list[str] | None,
    phone: str | None = None,
    farm_name: str | None = None,
    farm_area_acres: float | None = None,
) -> User:
    if name is not None:
        user.name = name
    if phone is not None:
        user.phone = phone
    if language is not None:
        user.language = language
    if user.farm is None:
        user.farm = Farm()
    if location is not None:
        user.farm.location = location
    if farm_name is not None:
        user.farm.name = farm_name
    if farm_area_acres is not None:
        user.farm.area_acres = farm_area_acres
    if latitude is not None:
        user.farm.latitude = latitude
    if longitude is not None:
        user.farm.longitude = longitude
    if crop_history is not None:
        user.farm.crop_history = crop_history
    session.commit()
    session.refresh(user)
    return user

def find_user_by_identifier(session: Session, identifier: str) -> User | None:
    trimmed = identifier.strip()
    trimmed_lower = trimmed.lower()
    conditions = [
        func.lower(User.email) == trimmed_lower,
        func.lower(User.pending_email) == trimmed_lower,
        User.phone == trimmed,
    ]
    digits = "".join(ch for ch in trimmed if ch.isdigit())
    if digits:
        conditions.append(User.phone == digits)
        if len(digits) >= 10:
            last10 = digits[-10:]
            conditions.append(User.phone == f"+91{last10}")
            conditions.append(User.phone == last10)
    return session.scalar(select(User).where(or_(*conditions)))

def get_user(session: Session, user_id: str) -> User | None:
    return session.get(User, user_id)
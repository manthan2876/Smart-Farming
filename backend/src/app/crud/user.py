from sqlalchemy.orm import Session
from sqlalchemy import or_, select

from app.models import (
    Farm,
    User,
)

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(
    session: Session,
    *,
    user_id: str,
    name: str,
    phone: str | None,
    email: str | None,
    password_hash: str,
    language: str,
    location: str | None,
    latitude: float | None,
    longitude: float | None,
    crop_history: list[str],
    farm_name: str | None = None,
    farm_area_acres: float | None = None,
) -> User:
    user = User(
        id=user_id,
        name=name,
        phone=phone,
        email=email,
        password_hash=password_hash,
        language=language,
    )
    user.farm = Farm(
        name=farm_name,
        location=location,
        area_acres=farm_area_acres,
        latitude=latitude,
        longitude=longitude,
        crop_history=crop_history,
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
    farm_name: str | None = None,
    farm_area_acres: float | None = None,
) -> User:
    if name is not None:
        user.name = name
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
    return session.scalar(
        select(User).where(or_(User.email == identifier, User.phone == identifier))
    )

def get_user(session: Session, user_id: str) -> User | None:
    return session.get(User, user_id)
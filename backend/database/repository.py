from __future__ import annotations

from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.database.models import (
    Farm,
    Feedback,
    Image,
    Prediction,
    Recommendation,
    User,
)


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


def find_user_by_identifier(session: Session, identifier: str) -> User | None:
    return session.scalar(
        select(User).where(or_(User.email == identifier, User.phone == identifier))
    )


def get_user(session: Session, user_id: str) -> User | None:
    return session.get(User, user_id)


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


def save_farm(session: Session, user: User, data: dict[str, Any]) -> Farm:
    if user.farm is None:
        user.farm = Farm(user_id=user.id)
    user.farm.name = data["name"]
    user.farm.location = data["location"]
    user.farm.area_acres = data["area_acres"]
    user.farm.latitude = data.get("latitude")
    user.farm.longitude = data.get("longitude")
    user.farm.crop_history = data.get("crop_history", [])
    session.add(user.farm)
    session.commit()
    session.refresh(user.farm)
    return user.farm


def record_prediction(
    session: Session, user_id: str, result: dict[str, Any]
) -> Prediction:
    user = session.get(User, user_id)
    if user is None:
        user = User(id=user_id)
        session.add(user)
        session.flush()

    image = result.get("image", {})
    crop = result.get("crop", {})
    disease = result.get("disease", {})
    severity = result.get("severity", {})
    image_record = Image(
        user_id=user_id,
        raw_path=str(image.get("raw_path", "")),
        processed_path=image.get("processed_path"),
        quality_score=image.get("quality_score"),
        blur_score=image.get("blur_score"),
        brightness_score=image.get("brightness_score"),
        leaf_detected=bool(image.get("leaf_detected", False)),
    )
    session.add(image_record)
    session.flush()
    prediction = Prediction(
        user_id=user_id,
        image_id=image_record.id,
        raw_path=str(image.get("raw_path", "")),
        processed_path=image.get("processed_path"),
        crop=crop.get("label"),
        crop_conf=crop.get("confidence"),
        disease=disease.get("label"),
        disease_conf=disease.get("confidence"),
        model_used=disease.get("model_used"),
        severity_pct=severity.get("percent"),
        result=result,
    )
    prediction.recommendation = Recommendation(
        fertilizer=result.get("recommendation", {}).get("fertilizer"),
        pesticide=result.get("recommendation", {}).get("pesticide"),
        irrigation=result.get("recommendation", {}).get("irrigation"),
        prevention_tips=result.get("recommendation", {}).get("prevention_tips"),
    )
    session.add(prediction)
    session.commit()
    session.refresh(prediction)
    return prediction


def get_prediction(
    session: Session, prediction_id: int, user_id: str
) -> Prediction | None:
    return session.scalar(
        select(Prediction).where(
            Prediction.id == prediction_id, Prediction.user_id == user_id
        )
    )


def list_predictions(
    session: Session, user_id: str, offset: int, limit: int
) -> list[Prediction]:
    return list(
        session.scalars(
            select(Prediction)
            .where(Prediction.user_id == user_id)
            .order_by(Prediction.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
    )


def add_feedback(
    session: Session,
    prediction: Prediction,
    is_correct: bool,
    farmer_note: str | None,
) -> Feedback:
    feedback = Feedback(
        prediction_id=prediction.id,
        is_correct=is_correct,
        farmer_note=farmer_note,
    )
    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    return feedback

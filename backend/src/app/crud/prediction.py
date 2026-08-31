from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Image,
    Prediction,
    Recommendation,
    User,
)

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
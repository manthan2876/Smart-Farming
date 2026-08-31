from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session

from app.models import (
    Farm,
    User,
)

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
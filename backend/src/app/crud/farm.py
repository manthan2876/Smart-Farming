from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import Farm, User, Plot


def save_farm(session: Session, user: User, data: dict[str, Any]) -> Farm:
    """Save or update farm metadata for a user."""
    if user.farm is None:
        user.farm = Farm(user_id=user.id)
    user.farm.name = data["name"]
    user.farm.location = data["location"]
    user.farm.area_acres = data["area_acres"]
    user.farm.latitude = data.get("latitude")
    user.farm.longitude = data.get("longitude")
    user.farm.crop_history = data.get("crop_history", [])
    user.farm.boundary = data.get("boundary")
    session.add(user.farm)
    session.commit()
    session.refresh(user.farm)
    return user.farm


def get_plot_by_id(session: Session, plot_id: int) -> Plot | None:
    """Retrieve a single plot by ID."""
    return session.get(Plot, plot_id)


def get_plot_by_name(session: Session, farm_id: int, name: str) -> Plot | None:
    """Check for existing plot with identical name under the same farm."""
    return session.scalar(
        select(Plot).where(Plot.farm_id == farm_id, Plot.name == name)
    )


def create_plot_record(
    session: Session,
    farm_id: int,
    name: str,
    crop: str | None,
    area_acres: float,
    status: str,
    geometry: dict | None,
) -> Plot:
    """Create and persist a new farm plot."""
    plot = Plot(
        farm_id=farm_id,
        name=name,
        crop=crop,
        area_acres=area_acres,
        status=status,
        geometry=geometry,
    )
    session.add(plot)
    session.commit()
    session.refresh(plot)
    return plot


def update_plot_record(
    session: Session,
    plot: Plot,
    name: str | None,
    crop: str | None,
    area_acres: float | None,
    status: str | None,
    geometry: dict | None,
) -> Plot:
    """Update existing plot attributes."""
    if name is not None:
        plot.name = name
    if crop is not None:
        plot.crop = crop
    if area_acres is not None:
        plot.area_acres = area_acres
    if status is not None:
        plot.status = status
    if geometry is not None:
        plot.geometry = geometry
    session.add(plot)
    session.commit()
    session.refresh(plot)
    return plot


def delete_plot_record(session: Session, plot: Plot) -> None:
    """Remove a plot from the database."""
    session.delete(plot)
    session.commit()

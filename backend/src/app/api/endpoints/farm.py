from __future__ import annotations

import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core import get_session
from app.schemas import FarmRequest, FarmResponse, PlotRequest, PlotResponse
from app.services.farm import (
    get_farmer_farm_data,
    update_farmer_farm_data,
    add_plot_to_farm,
    modify_plot_in_farm,
    remove_plot_from_farm,
    validate_geojson_polygon,
    plot_inside_farm,
)

# Backwards compatibility alias
_validate_geojson_polygon = validate_geojson_polygon
_plot_inside_farm = plot_inside_farm

__all__ = [
    "router",
    "_validate_geojson_polygon",
    "_plot_inside_farm",
    "validate_geojson_polygon",
    "plot_inside_farm",
]

logger = logging.getLogger("smart-farming.api.farm")
router = APIRouter(prefix="/farm", tags=["farm"])


def _enqueue_farm_transliteration(farm_id: int, name: str, location: str) -> None:
    from app.core.arq import enqueue_translation
    import asyncio
    try:
        asyncio.run(
            enqueue_translation(
                "farm",
                farm_id,
                {"name": name, "location": location or ""},
                name_fields=["name", "location"],
            )
        )
    except Exception:
        # Background transliteration failure must not fail the primary synchronous farm request
        pass


def _enqueue_plot_transliteration(plot_id: int, name: str) -> None:
    from app.core.arq import enqueue_translation
    import asyncio
    try:
        asyncio.run(
            enqueue_translation(
                "plot",
                plot_id,
                {"name": name},
                name_fields=["name"],
            )
        )
    except Exception:
        # Background transliteration failure must not fail the primary synchronous plot request
        pass


@router.get("", response_model=FarmResponse)
def get_farmer_farm(
    request: Request,
    lang: str | None = None,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> FarmResponse:
    """Retrieve farmer farm details, plots, and boundaries with localized overlays."""
    try:
        req_lang = lang or request.headers.get("accept-language")
        return get_farmer_farm_data(session, user_id, req_lang)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.exception("Database error loading farm for user %s", user_id)
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc


@router.put("", response_model=FarmResponse)
def save_farmer_farm(
    payload: FarmRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> FarmResponse:
    """Configure or update farm metadata and boundary polygon."""
    try:
        farm_res, farm_entity = update_farmer_farm_data(session, user_id, payload)
        background_tasks.add_task(
            _enqueue_farm_transliteration,
            farm_entity.id,
            farm_entity.name or "",
            farm_entity.location or "",
        )
        return farm_res
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        session.rollback()
        logger.exception("Database error saving farm for user %s", user_id)
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc


@router.post("/plots", response_model=PlotResponse, status_code=status.HTTP_201_CREATED)
def create_plot(
    payload: PlotRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> PlotResponse:
    """Add a new crop plot inside the verified farm boundary."""
    try:
        plot_res, plot_entity = add_plot_to_farm(session, user_id, payload)
        background_tasks.add_task(
            _enqueue_plot_transliteration,
            plot_entity.id,
            plot_entity.name,
        )
        return plot_res
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        session.rollback()
        logger.exception("Database error creating plot for user %s", user_id)
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc


@router.put("/plots/{plot_id}", response_model=PlotResponse)
def update_plot(
    plot_id: int,
    payload: PlotRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> PlotResponse:
    """Update plot metadata, assigned crop, or plot boundaries."""
    try:
        plot_res, plot_entity = modify_plot_in_farm(session, user_id, plot_id, payload)
        if payload.name:
            background_tasks.add_task(
                _enqueue_plot_transliteration,
                plot_entity.id,
                plot_entity.name,
            )
        return plot_res
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        session.rollback()
        logger.exception("Database error updating plot %s for user %s", plot_id, user_id)
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc


@router.delete("/plots/{plot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plot(
    plot_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    """Delete a plot from the farm."""
    try:
        remove_plot_from_farm(session, user_id, plot_id)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        session.rollback()
        logger.exception("Database error deleting plot %s for user %s", plot_id, user_id)
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc

from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.schemas import FarmRequest, FarmResponse, PlotRequest, PlotResponse
from app.crud import get_user, save_farm
from app.core import get_session

router = APIRouter(prefix="/farm", tags=["farm"])


def _point_inside_polygon(point: list[float], polygon: list[list[float]]) -> bool:
    longitude, latitude = point
    inside = False
    for index, current in enumerate(polygon):
        previous = polygon[index - 1]
        current_longitude, current_latitude = current
        previous_longitude, previous_latitude = previous
        intersects = ((current_latitude > latitude) != (previous_latitude > latitude)) and (
            longitude < (previous_longitude - current_longitude)
            * (latitude - current_latitude)
            / (previous_latitude - current_latitude)
            + current_longitude
        )
        if intersects:
            inside = not inside
    return inside


def _point_on_polygon_boundary(point: list[float], polygon: list[list[float]]) -> bool:
    longitude, latitude = point
    tolerance = 1e-8
    for index, current in enumerate(polygon[:-1]):
        next_point = polygon[index + 1]
        current_longitude, current_latitude = current
        next_longitude, next_latitude = next_point
        cross = (
            (longitude - current_longitude) * (next_latitude - current_latitude)
            - (latitude - current_latitude) * (next_longitude - current_longitude)
        )
        if abs(cross) <= tolerance and (
            min(current_longitude, next_longitude) - tolerance <= longitude <= max(current_longitude, next_longitude) + tolerance
            and min(current_latitude, next_latitude) - tolerance <= latitude <= max(current_latitude, next_latitude) + tolerance
        ):
            return True
    return False


def _plot_inside_farm(plot_geometry: dict | None, farm_boundary: dict | None) -> bool:
    if not plot_geometry or plot_geometry.get("type") != "Polygon":
        return False
    plot_ring = plot_geometry.get("coordinates", [[]])[0]
    farm_ring = (farm_boundary or {}).get("coordinates", [[]])[0]
    if len(plot_ring) < 4 or len(farm_ring) < 4:
        return False
    return all(
        _point_inside_polygon(point, farm_ring) or _point_on_polygon_boundary(point, farm_ring)
        for point in plot_ring[:-1]
    )

@router.get("", response_model=FarmResponse)
async def get_farmer_farm(
    user_id: str = Depends(get_current_user), session: Session = Depends(get_session)
) -> FarmResponse:
    try:
        user = get_user(session, user_id)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    if user is None or user.farm is None:
        raise HTTPException(status_code=404, detail="Farm has not been configured.")
    farm = user.farm
    return FarmResponse(
        id=farm.id,
        name=farm.name,
        location=farm.location,
        area_acres=farm.area_acres,
        latitude=farm.latitude,
        longitude=farm.longitude,
        crop_history=farm.crop_history or [],
        boundary=farm.boundary,
        plots=[{
            "id": p.id,
            "name": p.name,
            "crop": p.crop,
            "area_acres": p.area_acres,
            "status": p.status,
            "geometry": p.geometry,
        } for p in farm.plots]
    )

@router.put("", response_model=FarmResponse)
async def save_farmer_farm(
    payload: FarmRequest,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> FarmResponse:
    try:
        user = get_user(session, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="Farmer profile not found.")
        farm = save_farm(session, user, payload.model_dump())
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    return FarmResponse(
        id=farm.id,
        name=farm.name,
        location=farm.location,
        area_acres=farm.area_acres,
        latitude=farm.latitude,
        longitude=farm.longitude,
        crop_history=farm.crop_history or [],
        boundary=farm.boundary,
        plots=[{
            "id": p.id,
            "name": p.name,
            "crop": p.crop,
            "area_acres": p.area_acres,
            "status": p.status,
            "geometry": p.geometry,
        } for p in farm.plots]
    )



@router.post("/plots", response_model=PlotResponse)
async def create_plot(
    payload: PlotRequest,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> PlotResponse:
    from app.models.plot import Plot
    try:
        user = get_user(session, user_id)
        if not user or not user.farm:
            raise HTTPException(status_code=404, detail="Farm not found.")
        if not _plot_inside_farm(payload.geometry, user.farm.boundary):
            raise HTTPException(status_code=400, detail="Plot boundary must be inside the saved farm boundary.")
        new_plot = Plot(
            farm_id=user.farm.id,
            name=payload.name,
            crop=payload.crop,
            area_acres=payload.area_acres,
            status="healthy",
            geometry=payload.geometry
        )
        session.add(new_plot)
        session.commit()
        session.refresh(new_plot)
        return new_plot
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=503, detail="Database error.") from exc

@router.put("/plots/{plot_id}", response_model=PlotResponse)
async def update_plot(
    plot_id: int,
    payload: PlotRequest,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> PlotResponse:
    from app.models.plot import Plot
    try:
        user = get_user(session, user_id)
        if not user or not user.farm:
            raise HTTPException(status_code=404, detail="Farm not found.")
        plot = session.query(Plot).filter(Plot.id == plot_id, Plot.farm_id == user.farm.id).first()
        if not plot:
            raise HTTPException(status_code=404, detail="Plot not found.")
        if payload.geometry is not None and not _plot_inside_farm(payload.geometry, user.farm.boundary):
            raise HTTPException(status_code=400, detail="Plot boundary must be inside the saved farm boundary.")
        
        plot.name = payload.name
        plot.crop = payload.crop
        plot.area_acres = payload.area_acres
        if payload.geometry is not None:
            plot.geometry = payload.geometry
        session.commit()
        session.refresh(plot)
        return plot
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=503, detail="Database error.") from exc

@router.delete("/plots/{plot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plot(
    plot_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    from app.models.plot import Plot
    try:
        user = get_user(session, user_id)
        if not user or not user.farm:
            raise HTTPException(status_code=404, detail="Farm not found.")
        plot = session.query(Plot).filter(Plot.id == plot_id, Plot.farm_id == user.farm.id).first()
        if not plot:
            raise HTTPException(status_code=404, detail="Plot not found.")
        
        session.delete(plot)
        session.commit()
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=503, detail="Database error.") from exc

from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.schemas import FarmRequest, FarmResponse, PlotRequest, PlotResponse
from app.crud import get_user, save_farm
from app.core import get_session

router = APIRouter(prefix="/farm", tags=["farm"])


import math
from shapely.geometry import Polygon as ShapelyPolygon


def _validate_geojson_polygon(geom: dict | None) -> tuple[bool, str, float | None]:
    """Validate GeoJSON Polygon for closed rings, valid coordinates, and absence of self-intersections."""
    if not geom or not isinstance(geom, dict):
        return True, "No geometry", None
    if geom.get("type") != "Polygon":
        return False, "Geometry type must be 'Polygon'.", None
    coords = geom.get("coordinates")
    if not coords or not isinstance(coords, list) or len(coords) == 0:
        return False, "Polygon coordinates missing.", None
    ring = coords[0]
    if len(ring) < 4:
        return False, "Polygon ring must have at least 4 coordinates.", None
    if ring[0] != ring[-1]:
        return False, "LinearRing is not closed (first and last coordinate must be identical).", None
    
    # Coordinate range validation (-180 <= lon <= 180, -90 <= lat <= 90)
    for pt in ring:
        if not isinstance(pt, (list, tuple)) or len(pt) < 2:
            return False, "Invalid coordinate pair.", None
        lon, lat = float(pt[0]), float(pt[1])
        if not (-180.0 <= lon <= 180.0 and -90.0 <= lat <= 90.0):
            return False, f"Coordinates out of bounds: lon {lon}, lat {lat}.", None

    try:
        poly = ShapelyPolygon(ring)
        if not poly.is_valid:
            return False, "Polygon has self-intersections or is invalid.", None
        # Geodesic area calculation approximation in acres
        mean_lat = math.radians(sum(pt[1] for pt in ring) / len(ring))
        meters_per_deg_lat = 111132.92
        meters_per_deg_lon = 111412.84 * math.cos(mean_lat)
        proj_coords = [(pt[0] * meters_per_deg_lon, pt[1] * meters_per_deg_lat) for pt in ring]
        proj_poly = ShapelyPolygon(proj_coords)
        area_acres = round(proj_poly.area / 4046.8564224, 2)
        return True, "Valid", area_acres
    except Exception as exc:
        return False, f"Invalid geometry: {exc}", None


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

        data = payload.model_dump()
        if payload.boundary:
            valid, msg, calc_acres = _validate_geojson_polygon(payload.boundary)
            if not valid:
                raise HTTPException(status_code=422, detail=f"Invalid farm boundary: {msg}")
            if (data.get("area_acres") is None or data.get("area_acres") == 0) and calc_acres:
                data["area_acres"] = calc_acres

        farm = save_farm(session, user, data)
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
        
        calc_acres = None
        if payload.geometry:
            valid, msg, calc_acres = _validate_geojson_polygon(payload.geometry)
            if not valid:
                raise HTTPException(status_code=422, detail=f"Invalid plot geometry: {msg}")

        # Check containment inside farm if farm boundary exists
        if payload.geometry and user.farm.boundary:
            try:
                farm_poly = ShapelyPolygon(user.farm.boundary.get("coordinates", [[]])[0])
                plot_poly = ShapelyPolygon(payload.geometry.get("coordinates", [[]])[0])
                if not farm_poly.contains(plot_poly) and not farm_poly.intersects(plot_poly):
                    raise HTTPException(status_code=400, detail="Plot boundary must be within the saved farm boundary.")
            except HTTPException:
                raise
            except Exception:
                pass

        final_area = payload.area_acres or calc_acres or 0.0
        new_plot = Plot(
            farm_id=user.farm.id,
            name=payload.name,
            crop=payload.crop,
            area_acres=final_area,
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

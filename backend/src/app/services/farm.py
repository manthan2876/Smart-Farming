from __future__ import annotations

import logging
import math
from fastapi import HTTPException
from shapely.geometry import Polygon as ShapelyPolygon  # type: ignore[import-untyped]
from sqlalchemy.orm import Session

from app.crud.farm import (
    save_farm,
    get_plot_by_id,
    get_plot_by_name,
    create_plot_record,
    update_plot_record,
    delete_plot_record,
)
from app.crud.user import get_user
from app.models import Farm, Plot
from app.schemas import FarmRequest, FarmResponse, PlotRequest, PlotResponse
from app.services.translation.overlay import overlay_dict_translations, overlay_entity_translations

logger = logging.getLogger("smart-farming.services.farm")


def validate_geojson_polygon(geom: dict | None) -> tuple[bool, str, float | None]:
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
        mean_lat = math.radians(sum(pt[1] for pt in ring) / len(ring))
        meters_per_deg_lat = 111132.92
        meters_per_deg_lon = 111412.84 * math.cos(mean_lat)
        proj_coords = [(pt[0] * meters_per_deg_lon, pt[1] * meters_per_deg_lat) for pt in ring]
        proj_poly = ShapelyPolygon(proj_coords)
        area_acres = round(proj_poly.area / 4046.8564224, 2)
        return True, "Valid", area_acres
    except Exception as exc:
        return False, f"Invalid geometry: {exc}", None


def plot_inside_farm(plot_geom: dict | None, farm_geom: dict | None) -> bool:
    """Check if plot geometry is contained within farm boundary."""
    if not plot_geom or not farm_geom:
        return True
    try:
        farm_ring = farm_geom.get("coordinates", [[]])[0]
        plot_ring = plot_geom.get("coordinates", [[]])[0]
        if not farm_ring or not plot_ring or len(farm_ring) < 3 or len(plot_ring) < 3:
            return True
        farm_poly = ShapelyPolygon(farm_ring)
        plot_poly = ShapelyPolygon(plot_ring)
        buffered = farm_poly.buffer(1e-7)
        return buffered.contains(plot_poly) or buffered.covers(plot_poly)
    except Exception:
        return True


def get_farmer_farm_data(
    session: Session,
    user_id: str,
    requested_language: str | None = None,
) -> FarmResponse:
    """Load farmer's farm and plot data with localized name overlays."""
    user = get_user(session, user_id)
    if user is None or user.farm is None:
        raise HTTPException(status_code=404, detail="Farm has not been configured.")

    farm = user.farm
    plot_items = [{
        "id": p.id,
        "name": p.name,
        "crop": p.crop,
        "area_acres": p.area_acres,
        "status": p.status,
        "geometry": p.geometry,
    } for p in farm.plots]

    req_lang = requested_language or user.language
    overlay_entity_translations(
        session, plot_items, "plot", lambda x: x["id"], ["name"], req_lang, name_fields=["name"]
    )

    farm_data = {
        "id": farm.id,
        "name": farm.name,
        "location": farm.location,
        "area_acres": farm.area_acres,
        "latitude": farm.latitude,
        "longitude": farm.longitude,
        "crop_history": farm.crop_history or [],
        "boundary": farm.boundary,
        "plots": plot_items,
    }
    overlay_dict_translations(
        session, farm_data, "farm", farm.id, ["name", "location"], req_lang, name_fields=["name", "location"]
    )
    return FarmResponse(**farm_data)


def update_farmer_farm_data(
    session: Session,
    user_id: str,
    payload: FarmRequest,
) -> tuple[FarmResponse, Farm]:
    """Validate and persist farm updates."""
    user = get_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Farmer profile not found.")

    data = payload.model_dump()
    if payload.reset_boundary:
        data["boundary"] = None
    elif payload.boundary:
        valid, msg, calc_acres = validate_geojson_polygon(payload.boundary)
        if not valid:
            raise HTTPException(status_code=422, detail=f"Invalid farm boundary: {msg}")
        if (data.get("area_acres") is None or data.get("area_acres") == 0) and calc_acres:
            data["area_acres"] = calc_acres

    farm = save_farm(session, user, data)
    farm_res = FarmResponse(
        id=farm.id,
        name=farm.name,
        location=farm.location,
        area_acres=farm.area_acres,
        latitude=farm.latitude,
        longitude=farm.longitude,
        crop_history=farm.crop_history or [],
        boundary=farm.boundary,
        plots=[
            PlotResponse(
                id=p.id,
                name=p.name,
                crop=p.crop,
                area_acres=p.area_acres,
                status=p.status,
                geometry=p.geometry,
            )
            for p in farm.plots
        ],
    )
    return farm_res, farm


def add_plot_to_farm(
    session: Session,
    user_id: str,
    payload: PlotRequest,
) -> tuple[PlotResponse, Plot]:
    """Validate plot boundary containment and persist new plot."""
    user = get_user(session, user_id)
    if user is None or user.farm is None:
        raise HTTPException(status_code=404, detail="Farm must be configured before adding plots.")

    existing = get_plot_by_name(session, user.farm.id, payload.name)
    if existing:
        raise HTTPException(status_code=409, detail=f"A plot named '{payload.name}' already exists.")

    calc_acres = None
    if payload.geometry:
        valid, msg, calc_acres = validate_geojson_polygon(payload.geometry)
        if not valid:
            raise HTTPException(status_code=422, detail=f"Invalid plot geometry: {msg}")
        if user.farm.boundary and not plot_inside_farm(payload.geometry, user.farm.boundary):
            raise HTTPException(
                status_code=400,
                detail="Plot boundary must be inside the saved farm boundary.",
            )

    plot = create_plot_record(
        session=session,
        farm_id=user.farm.id,
        name=payload.name,
        crop=payload.crop,
        area_acres=calc_acres or payload.area_acres or 0.0,
        status="active",
        geometry=payload.geometry,
    )
    plot_res = PlotResponse(
        id=plot.id,
        name=plot.name,
        crop=plot.crop,
        area_acres=plot.area_acres,
        status=plot.status,
        geometry=plot.geometry,
    )
    return plot_res, plot


def modify_plot_in_farm(
    session: Session,
    user_id: str,
    plot_id: int,
    payload: PlotRequest,
) -> tuple[PlotResponse, Plot]:
    """Validate ownership and updates to an existing plot."""
    user = get_user(session, user_id)
    if user is None or user.farm is None:
        raise HTTPException(status_code=404, detail="Farm not found.")

    plot = get_plot_by_id(session, plot_id)
    if not plot or plot.farm_id != user.farm.id:
        raise HTTPException(status_code=404, detail="Plot not found.")

    new_geom = plot.geometry
    new_area = payload.area_acres if payload.area_acres is not None else plot.area_acres
    if payload.reset_geometry:
        new_geom = None
    elif payload.geometry is not None:
        valid, msg, calc_acres = validate_geojson_polygon(payload.geometry)
        if not valid:
            raise HTTPException(status_code=422, detail=f"Invalid plot geometry: {msg}")
        if user.farm.boundary and not plot_inside_farm(payload.geometry, user.farm.boundary):
            raise HTTPException(
                status_code=400,
                detail="Plot boundary must be inside the saved farm boundary.",
            )
        new_geom = payload.geometry
        if (payload.area_acres is None or payload.area_acres == 0) and calc_acres:
            new_area = calc_acres

    updated = update_plot_record(
        session=session,
        plot=plot,
        name=payload.name,
        crop=payload.crop,
        area_acres=new_area,
        status=None,
        geometry=new_geom,
    )
    plot_res = PlotResponse(
        id=updated.id,
        name=updated.name,
        crop=updated.crop,
        area_acres=updated.area_acres,
        status=updated.status,
        geometry=updated.geometry,
    )
    return plot_res, updated


def remove_plot_from_farm(session: Session, user_id: str, plot_id: int) -> None:
    """Validate ownership and remove a plot."""
    user = get_user(session, user_id)
    if user is None or user.farm is None:
        raise HTTPException(status_code=404, detail="Farm not found.")

    plot = get_plot_by_id(session, plot_id)
    if not plot or plot.farm_id != user.farm.id:
        raise HTTPException(status_code=404, detail="Plot not found.")

    delete_plot_record(session, plot)

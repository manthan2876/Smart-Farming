from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.schemas import FarmRequest, FarmResponse, PlotRequest, PlotResponse
from app.crud import get_user, save_farm
from app.core import get_session

router = APIRouter(prefix="/farm", tags=["farm"])

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
        plots=[{
            "id": p.id,
            "name": p.name,
            "crop": p.crop,
            "area_acres": p.area_acres,
            "status": p.status
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
        plots=[{
            "id": p.id,
            "name": p.name,
            "crop": p.crop,
            "area_acres": p.area_acres,
            "status": p.status
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
        new_plot = Plot(
            farm_id=user.farm.id,
            name=payload.name,
            crop=payload.crop,
            area_acres=payload.area_acres,
            status="healthy"
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
        
        plot.name = payload.name
        plot.crop = payload.crop
        plot.area_acres = payload.area_acres
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

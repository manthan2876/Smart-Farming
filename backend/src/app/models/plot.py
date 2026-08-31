from datetime import datetime, timezone
from app.core import Base
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Plot(Base):
    __tablename__ = "plots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    crop: Mapped[str | None] = mapped_column(String(100), nullable=True)
    area_acres: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="healthy")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default = lambda : datetime.now(timezone.utc)
    )

    farm: Mapped["Farm"] = relationship(back_populates="plots")
    predictions: Mapped[list["Prediction"]] = relationship(back_populates="plot")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="plot")
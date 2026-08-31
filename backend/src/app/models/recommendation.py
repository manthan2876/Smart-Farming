from app.core import Base
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prediction_id: Mapped[int] = mapped_column(
        ForeignKey("predictions.id"), unique=True
    )
    fertilizer: Mapped[str | None] = mapped_column(Text, nullable=True)
    pesticide: Mapped[str | None] = mapped_column(Text, nullable=True)
    irrigation: Mapped[str | None] = mapped_column(Text, nullable=True)
    prevention_tips: Mapped[str | None] = mapped_column(Text, nullable=True)

    prediction: Mapped["Prediction"] = relationship(back_populates="recommendation")
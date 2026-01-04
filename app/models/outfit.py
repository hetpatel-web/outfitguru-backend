from datetime import date, datetime
from typing import List

from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey, Integer, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import OutfitFeedback


class Outfit(Base):
    __tablename__ = "outfits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    item_ids: Mapped[List[int]] = mapped_column(JSON, nullable=False)
    feedback: Mapped[OutfitFeedback] = mapped_column(
        SAEnum(OutfitFeedback, name="outfit_feedback"), nullable=False, default=OutfitFeedback.NONE
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="outfits")

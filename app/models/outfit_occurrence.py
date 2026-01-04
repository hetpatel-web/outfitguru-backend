from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import NegativeReason, OutfitStatus


class OutfitOccurrence(Base):
    __tablename__ = "outfit_occurrences"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_outfit_occurrence_user_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    outfit_id: Mapped[Optional[int]] = mapped_column(ForeignKey("outfits.id"), nullable=True)
    status: Mapped[OutfitStatus] = mapped_column(
        SAEnum(OutfitStatus, name="outfit_occurrence_status"),
        nullable=False,
        default=OutfitStatus.PLANNED,
        server_default=OutfitStatus.PLANNED.value,
    )
    negative_reason: Mapped[Optional[NegativeReason]] = mapped_column(
        SAEnum(NegativeReason, name="negative_reason"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    outfit: Mapped[Optional["Outfit"]] = relationship("Outfit")
    user: Mapped["User"] = relationship("User", back_populates="outfit_occurrences")

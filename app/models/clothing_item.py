from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ClothingCategory, ColorFamily, Season


class ClothingItem(Base):
    __tablename__ = "clothing_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    category: Mapped[ClothingCategory] = mapped_column(
        SAEnum(ClothingCategory, name="clothing_category"), nullable=False
    )
    subtype: Mapped[str] = mapped_column(String, nullable=False, default="General", server_default="General")
    color: Mapped[str] = mapped_column(String, nullable=False)
    color_family: Mapped[ColorFamily] = mapped_column(
        SAEnum(ColorFamily, name="color_family"),
        nullable=False,
        default=ColorFamily.OTHER,
        server_default=ColorFamily.OTHER.value,
    )
    season: Mapped[Season] = mapped_column(
        SAEnum(Season, name="season"),
        nullable=False,
        default=Season.ALL_SEASON,
        server_default=Season.ALL_SEASON.value,
    )
    image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="clothing_items")

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.clothing_item import ClothingCategory


class ClothingItemBase(BaseModel):
    category: ClothingCategory
    color: str = Field(min_length=1)
    image_url: Optional[str] = None
    notes: Optional[str] = None


class ClothingItemCreate(ClothingItemBase):
    pass


class ClothingItemResponse(ClothingItemBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

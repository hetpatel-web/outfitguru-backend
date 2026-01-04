from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import ClothingCategory, ColorFamily, Season


class ClothingItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    category: ClothingCategory
    subtype: str = Field(default="General", min_length=1)
    color: str = Field(min_length=1)
    color_family: ColorFamily = ColorFamily.OTHER
    season: Season = Season.ALL_SEASON
    image_url: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("name", "subtype", "color")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class ClothingItemCreate(ClothingItemBase):
    pass


class ClothingItemUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=80)
    category: Optional[ClothingCategory] = None
    subtype: Optional[str] = Field(default=None, min_length=1)
    color: Optional[str] = Field(default=None, min_length=1)
    color_family: Optional[ColorFamily] = None
    season: Optional[Season] = None
    image_url: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("name", "subtype", "color")
    @classmethod
    def strip_optional_text(cls, value: Optional[str]) -> Optional[str]:
        return value.strip() if value is not None else value


class ClothingItemResponse(ClothingItemBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class WardrobeCategory(BaseModel):
    slug: ClothingCategory
    label: str
    subtypes: list[str]


class WardrobeCategoriesResponse(BaseModel):
    categories: list[WardrobeCategory]
    color_families: list[str]
    seasons: list[str]

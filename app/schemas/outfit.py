from datetime import date, datetime
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import OutfitFeedback


class OutfitResponse(BaseModel):
    id: int
    date: date
    item_ids: List[int] = Field(default_factory=list)
    feedback: OutfitFeedback
    created_at: datetime
    reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OutfitFeedbackUpdate(BaseModel):
    feedback: OutfitFeedback


class NeedMoreItemsResponse(BaseModel):
    status: Literal["need_more_items"] = "need_more_items"
    missing_categories: List[str]
    message: str


RecommendationResponse = Union[OutfitResponse, NeedMoreItemsResponse]

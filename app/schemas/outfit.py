from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.outfit import OutfitFeedback


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

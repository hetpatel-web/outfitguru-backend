from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import NegativeReason, OutfitStatus
from app.schemas.outfit import OutfitResponse


class OutfitOccurrenceResponse(BaseModel):
    id: int
    user_id: int
    date: date
    outfit_id: Optional[int]
    status: OutfitStatus
    negative_reason: Optional[NegativeReason] = None
    created_at: datetime
    outfit: Optional[OutfitResponse] = None

    model_config = ConfigDict(from_attributes=True)


class MonthCalendarResponse(BaseModel):
    occurrences: list[OutfitOccurrenceResponse]


class DayCalendarResponse(BaseModel):
    occurrence: Optional[OutfitOccurrenceResponse]


class ConfirmWornRequest(BaseModel):
    date: date
    worn: bool = True
    negative_reason: Optional[NegativeReason] = None

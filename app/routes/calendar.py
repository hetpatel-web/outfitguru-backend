from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.calendar import ConfirmWornRequest, DayCalendarResponse, MonthCalendarResponse, OutfitOccurrenceResponse
from app.services.calendar import confirm_worn, get_day_occurrence, get_month_occurrences, plan_tomorrow
from app.utils.deps import get_current_user, get_db

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/month", response_model=MonthCalendarResponse)
def get_calendar_month(
    year: int,
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    occurrences = get_month_occurrences(db, current_user.id, year, month)
    return {"occurrences": occurrences}


@router.get("/day", response_model=DayCalendarResponse)
def get_calendar_day(
    target_date: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    occurrence = get_day_occurrence(db, current_user.id, target_date)
    return {"occurrence": occurrence}


@router.post("/plan-tomorrow", response_model=OutfitOccurrenceResponse, status_code=status.HTTP_200_OK)
def plan_for_tomorrow(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return plan_tomorrow(db, current_user.id)


@router.post("/confirm-worn", response_model=OutfitOccurrenceResponse)
def confirm_outfit_worn(
    payload: ConfirmWornRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    occurrence = confirm_worn(db, current_user.id, payload.date, payload.worn, payload.negative_reason)
    return occurrence

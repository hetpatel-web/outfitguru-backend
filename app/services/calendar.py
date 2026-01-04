from calendar import monthrange
from datetime import date, timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.enums import NegativeReason, OutfitStatus
from app.models.outfit import Outfit
from app.models.outfit_occurrence import OutfitOccurrence


def _occurrence_query(db: Session, user_id: int):
    return (
        db.query(OutfitOccurrence)
        .options(joinedload(OutfitOccurrence.outfit))
        .filter(OutfitOccurrence.user_id == user_id)
    )


def get_month_occurrences(db: Session, user_id: int, year: int, month: int):
    try:
        start = date(year, month, 1)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid year or month.")

    last_day = monthrange(year, month)[1]
    end = date(year, month, last_day)

    return (
        _occurrence_query(db, user_id)
        .filter(OutfitOccurrence.date >= start, OutfitOccurrence.date <= end)
        .order_by(OutfitOccurrence.date.asc())
        .all()
    )


def get_day_occurrence(db: Session, user_id: int, target_date: date) -> Optional[OutfitOccurrence]:
    return (
        _occurrence_query(db, user_id)
        .filter(OutfitOccurrence.date == target_date)
        .first()
    )


def _latest_outfit(db: Session, user_id: int) -> Optional[Outfit]:
    return (
        db.query(Outfit)
        .filter(Outfit.user_id == user_id)
        .order_by(Outfit.date.desc(), Outfit.created_at.desc())
        .first()
    )


def plan_outfit_for_date(db: Session, user_id: int, target_date: date) -> OutfitOccurrence:
    latest_outfit = _latest_outfit(db, user_id)
    if not latest_outfit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No outfit available to plan. Request a recommendation first.",
        )

    occurrence = (
        _occurrence_query(db, user_id)
        .filter(OutfitOccurrence.date == target_date)
        .first()
    )

    if not occurrence:
        occurrence = OutfitOccurrence(
            user_id=user_id,
            date=target_date,
            outfit_id=latest_outfit.id,
            status=OutfitStatus.PLANNED,
        )
        db.add(occurrence)
    else:
        occurrence.outfit_id = latest_outfit.id
        occurrence.status = OutfitStatus.PLANNED
        occurrence.negative_reason = None

    db.commit()
    db.refresh(occurrence)
    occurrence.outfit = latest_outfit
    return occurrence


def plan_tomorrow(db: Session, user_id: int) -> OutfitOccurrence:
    tomorrow = date.today() + timedelta(days=1)
    return plan_outfit_for_date(db, user_id, tomorrow)


def confirm_worn(
    db: Session,
    user_id: int,
    target_date: date,
    worn: bool = True,
    negative_reason: Optional[NegativeReason] = None,
) -> OutfitOccurrence:
    occurrence = (
        _occurrence_query(db, user_id)
        .filter(OutfitOccurrence.date == target_date)
        .first()
    )

    if not occurrence:
        occurrence = OutfitOccurrence(user_id=user_id, date=target_date, status=OutfitStatus.PLANNED)
        db.add(occurrence)
        db.flush()

    if not worn and not negative_reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please choose a reason if you skipped this outfit.",
        )

    occurrence.status = OutfitStatus.WORN
    occurrence.negative_reason = negative_reason if not worn else None

    db.commit()
    db.refresh(occurrence)
    return occurrence

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.clothing_item import ClothingItem
from app.models.enums import ClothingCategory, ColorFamily, Season
from app.models.outfit import Outfit
from app.models.user import User
from app.schemas.clothing_item import ClothingItemCreate, ClothingItemResponse, ClothingItemUpdate, WardrobeCategoriesResponse
from app.services.wardrobe_catalog import (
    get_color_families,
    get_seasons,
    get_wardrobe_categories,
    valid_subtypes_for,
)
from app.utils.deps import get_current_user, get_db

router = APIRouter(prefix="/wardrobe", tags=["wardrobe"])


def _validate_metadata(category: ClothingCategory, subtype: str, color_family: str, season: str):
    allowed_subtypes = valid_subtypes_for(category)
    if allowed_subtypes and subtype not in allowed_subtypes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid subtype for this category.",
        )
    if color_family not in get_color_families():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid color_family. Refer to /wardrobe/categories.",
        )
    if season not in get_seasons():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid season. Refer to /wardrobe/categories.",
        )


def _get_item_or_404(db: Session, user_id: int, item_id: int) -> ClothingItem:
    item = db.query(ClothingItem).filter(ClothingItem.id == item_id, ClothingItem.user_id == user_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found.")
    return item


@router.post("/items", response_model=ClothingItemResponse, status_code=status.HTTP_201_CREATED)
def create_clothing_item(
    item_in: ClothingItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    _validate_metadata(item_in.category, item_in.subtype or "General", item_in.color_family.value, item_in.season.value)
    item = ClothingItem(**item_in.model_dump(), user_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/items", response_model=List[ClothingItemResponse])
def list_clothing_items(
    category: Optional[ClothingCategory] = Query(default=None),
    q: Optional[str] = Query(default=None, min_length=1),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ClothingItem).filter(ClothingItem.user_id == current_user.id)
    if category:
        query = query.filter(ClothingItem.category == category)
    if q:
        like_term = f"%{q.strip()}%"
        query = query.filter(or_(ClothingItem.name.ilike(like_term), ClothingItem.subtype.ilike(like_term)))
    items = (
        query.order_by(ClothingItem.created_at.desc()).offset(offset).limit(limit).all()
    )
    return items


@router.get("/items/{item_id}", response_model=ClothingItemResponse)
def get_clothing_item(
    item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return _get_item_or_404(db, current_user.id, item_id)


@router.patch("/items/{item_id}", response_model=ClothingItemResponse)
def update_clothing_item(
    item_id: int,
    item_update: ClothingItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = _get_item_or_404(db, current_user.id, item_id)
    payload = item_update.model_dump(exclude_unset=True)

    new_category = payload.get("category", item.category)
    new_subtype = payload.get("subtype", item.subtype or "General")
    new_color_family_value = payload.get("color_family", item.color_family)
    new_season_value = payload.get("season", item.season)

    color_family_str = new_color_family_value.value if isinstance(new_color_family_value, ColorFamily) else str(new_color_family_value)
    season_str = new_season_value.value if isinstance(new_season_value, Season) else str(new_season_value)

    _validate_metadata(
        new_category,
        new_subtype or "General",
        color_family_str,
        season_str,
    )

    for field, value in payload.items():
        setattr(item, field, value)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_clothing_item(
    item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    item = _get_item_or_404(db, current_user.id, item_id)
    # Prevent deleting items used in outfits
    outfits = (
        db.query(Outfit)
        .filter(Outfit.user_id == current_user.id)
        .all()
    )
    if any(item.id in (outfit.item_ids or []) for outfit in outfits):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This item is used in saved outfits. Remove it from outfits first.",
        )

    db.delete(item)
    db.commit()
    return None


@router.get("/categories", response_model=WardrobeCategoriesResponse)
def get_categories():
    return {
        "categories": get_wardrobe_categories(),
        "color_families": get_color_families(),
        "seasons": get_seasons(),
    }

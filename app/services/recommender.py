from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.clothing_item import ClothingCategory, ClothingItem
from app.models.outfit import Outfit, OutfitFeedback


class RecommendationError(Exception):
    def __init__(self, missing_categories: List[str]):
        self.missing_categories = missing_categories
        super().__init__("Missing required wardrobe items.")


def _latest_item_for_category(db: Session, user_id: int, category: ClothingCategory) -> Optional[ClothingItem]:
    return (
        db.query(ClothingItem)
        .filter(ClothingItem.user_id == user_id, ClothingItem.category == category)
        .order_by(ClothingItem.created_at.desc())
        .first()
    )


def generate_outfit_recommendation(db: Session, user_id: int) -> Outfit:
    required = [ClothingCategory.TOP, ClothingCategory.BOTTOM, ClothingCategory.FOOTWEAR]
    chosen_items: List[ClothingItem] = []
    missing: List[str] = []

    for category in required:
        item = _latest_item_for_category(db, user_id, category)
        if not item:
            missing.append(category.value)
        else:
            chosen_items.append(item)

    if missing:
        raise RecommendationError(missing)

    outerwear = _latest_item_for_category(db, user_id, ClothingCategory.OUTERWEAR)
    if outerwear:
        chosen_items.append(outerwear)

    item_ids = [item.id for item in chosen_items]
    outfit = Outfit(
        user_id=user_id,
        date=date.today(),
        item_ids=item_ids,
        feedback=OutfitFeedback.NONE,
    )
    db.add(outfit)
    db.commit()
    db.refresh(outfit)
    return outfit

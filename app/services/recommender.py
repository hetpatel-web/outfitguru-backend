from datetime import date, datetime
from typing import List, Optional, Sequence

from sqlalchemy.orm import Session

from app.models.clothing_item import ClothingCategory, ClothingItem
from app.models.outfit import Outfit, OutfitFeedback


class RecommendationError(Exception):
    def __init__(self, missing_categories: List[str]):
        self.missing_categories = missing_categories
        super().__init__("Missing required wardrobe items.")


def _items_for_category(db: Session, user_id: int, category: ClothingCategory) -> List[ClothingItem]:
    return (
        db.query(ClothingItem)
        .filter(ClothingItem.user_id == user_id, ClothingItem.category == category)
        .order_by(ClothingItem.created_at.asc())
        .all()
    )


def generate_outfit_recommendation(db: Session, user_id: int) -> Outfit:
    required = [ClothingCategory.TOP, ClothingCategory.BOTTOM, ClothingCategory.FOOTWEAR]
    optional = [ClothingCategory.OUTERWEAR]
    missing: List[str] = []

    outfits: Sequence[Outfit] = (
        db.query(Outfit).filter(Outfit.user_id == user_id).order_by(Outfit.created_at.desc()).all()
    )
    last_outfit: Optional[Outfit] = outfits[0] if outfits else None

    last_used: dict[int, datetime] = {}
    for outfit in outfits:
        for item_id in outfit.item_ids:
            if item_id not in last_used:
                last_used[item_id] = outfit.created_at

    def pick_item(category: ClothingCategory) -> Optional[ClothingItem]:
        candidates = _items_for_category(db, user_id, category)
        if not candidates:
            missing.append(category.value)
            return None
        # Sort least recently used first (never used -> oldest last use -> newest last use)
        candidates.sort(
            key=lambda item: (
                0 if item.id not in last_used else 1,
                last_used.get(item.id) or datetime.min,
            )
        )
        return candidates

    selected: List[ClothingItem] = []
    category_options: dict[ClothingCategory, List[ClothingItem]] = {}

    for category in required:
        options = pick_item(category)
        if options:
            category_options[category] = options
            selected.append(options[0])

    if missing:
        raise RecommendationError(missing)

    # Optional outerwear
    outerwear_options = pick_item(ClothingCategory.OUTERWEAR)
    if outerwear_options:
        category_options[ClothingCategory.OUTERWEAR] = outerwear_options
        selected.append(outerwear_options[0])

    def current_item_ids(items: List[ClothingItem]) -> List[int]:
        return [item.id for item in items]

    # Avoid repeating the most recent outfit when alternatives exist
    if last_outfit:
        last_ids = set(last_outfit.item_ids)
        if set(current_item_ids(selected)) == last_ids:
            for cat, options in category_options.items():
                if len(options) > 1:
                    selected_copy = selected.copy()
                    for idx, item in enumerate(selected_copy):
                        if item.category == cat:
                            selected_copy[idx] = options[1]
                            break
                    if set(current_item_ids(selected_copy)) != last_ids:
                        selected = selected_copy
                        break

    item_ids = current_item_ids(selected)

    outfit = Outfit(
        user_id=user_id,
        date=date.today(),
        item_ids=item_ids,
        feedback=OutfitFeedback.NONE,
    )
    db.add(outfit)
    db.commit()
    db.refresh(outfit)

    applied_rules: List[str] = ["used least-recently-worn items per category"]
    if last_outfit and set(item_ids) != set(last_outfit.item_ids):
        applied_rules.append("avoided repeating your last outfit")
    elif last_outfit:
        applied_rules.append("no alternative to avoid last outfit")

    reason = f"Selected items because we {' and '.join(applied_rules)}."
    setattr(outfit, "reason", reason)

    return outfit

from datetime import date, datetime
from typing import List, Optional, Sequence

from sqlalchemy.orm import Session

from app.models.clothing_item import ClothingItem
from app.models.enums import ClothingCategory, OutfitFeedback
from app.models.outfit import Outfit


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
    outfits: Sequence[Outfit] = (
        db.query(Outfit).filter(Outfit.user_id == user_id).order_by(Outfit.created_at.desc()).all()
    )
    last_outfit: Optional[Outfit] = outfits[0] if outfits else None

    last_used: dict[int, datetime] = {}
    for outfit in outfits:
        for item_id in outfit.item_ids:
            if item_id not in last_used:
                last_used[item_id] = outfit.created_at

    def sorted_candidates(category: ClothingCategory) -> List[ClothingItem]:
        candidates = _items_for_category(db, user_id, category)
        candidates.sort(
            key=lambda item: (
                0 if item.id not in last_used else 1,
                last_used.get(item.id) or datetime.min,
            )
        )
        return candidates

    selected: List[ClothingItem] = []
    category_options: dict[ClothingCategory, List[ClothingItem]] = {}

    footwear_options = sorted_candidates(ClothingCategory.FOOTWEAR)
    one_piece_options = sorted_candidates(ClothingCategory.ONE_PIECE)
    top_options = sorted_candidates(ClothingCategory.TOP)
    bottom_options = sorted_candidates(ClothingCategory.BOTTOM)
    outerwear_options = sorted_candidates(ClothingCategory.OUTERWEAR)
    missing: List[str] = []

    if not footwear_options:
        missing.append(ClothingCategory.FOOTWEAR.value)

    separates_ready = bool(top_options) and bool(bottom_options)
    one_piece_ready = bool(one_piece_options)

    if separates_ready:
        category_options[ClothingCategory.TOP] = top_options
        category_options[ClothingCategory.BOTTOM] = bottom_options
        selected.extend([top_options[0], bottom_options[0]])
    elif one_piece_ready:
        category_options[ClothingCategory.ONE_PIECE] = one_piece_options
        selected.append(one_piece_options[0])
    else:
        if not one_piece_ready:
            missing.append(ClothingCategory.ONE_PIECE.value)
        if not separates_ready:
            if not top_options:
                missing.append(ClothingCategory.TOP.value)
            if not bottom_options:
                missing.append(ClothingCategory.BOTTOM.value)

    if footwear_options:
        category_options[ClothingCategory.FOOTWEAR] = footwear_options
        selected.append(footwear_options[0])

    if outerwear_options:
        category_options[ClothingCategory.OUTERWEAR] = outerwear_options
        selected.append(outerwear_options[0])

    if missing:
        raise RecommendationError(sorted(set(missing)))

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

    core_mix = "one-piece + footwear" if any(
        item.category == ClothingCategory.ONE_PIECE for item in selected
    ) else "top + bottom + footwear"
    applied_rules: List[str] = [f"kept required mix ({core_mix})", "used least-recently-worn items per category"]
    if last_outfit and set(item_ids) != set(last_outfit.item_ids):
        applied_rules.append("avoided repeating your last outfit")
    elif last_outfit:
        applied_rules.append("no alternative to avoid last outfit")

    reason = f"Selected items because we {' and '.join(applied_rules)}."
    setattr(outfit, "reason", reason)

    return outfit

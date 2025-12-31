from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.models.clothing_item import ClothingItem
from app.models.user import User
from app.schemas.clothing_item import ClothingItemCreate, ClothingItemResponse
from app.utils.deps import get_current_user, get_db

router = APIRouter(prefix="/wardrobe", tags=["wardrobe"])


@router.post("/items", response_model=ClothingItemResponse, status_code=status.HTTP_201_CREATED)
def create_clothing_item(
    item_in: ClothingItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    item = ClothingItem(**item_in.model_dump(), user_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/items", response_model=List[ClothingItemResponse])
def list_clothing_items(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = db.query(ClothingItem).filter(ClothingItem.user_id == current_user.id).order_by(ClothingItem.created_at.desc()).all()
    return items

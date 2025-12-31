from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.outfit import Outfit
from app.models.user import User
from app.schemas.outfit import OutfitFeedbackUpdate, OutfitResponse
from app.services.recommender import RecommendationError, generate_outfit_recommendation
from app.utils.deps import get_current_user, get_db

router = APIRouter(prefix="/outfits", tags=["outfits"])


@router.post("/recommendation", response_model=OutfitResponse, status_code=status.HTTP_201_CREATED)
def create_recommendation(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        outfit = generate_outfit_recommendation(db, current_user.id)
    except RecommendationError as err:
        missing = ", ".join(err.missing_categories)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Add at least one item in these categories before requesting a recommendation: {missing}.",
        )
    return outfit


@router.post("/{outfit_id}/feedback", response_model=OutfitResponse)
def set_outfit_feedback(
    outfit_id: int,
    feedback_update: OutfitFeedbackUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id, Outfit.user_id == current_user.id).first()
    if not outfit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found.")

    outfit.feedback = feedback_update.feedback
    db.commit()
    db.refresh(outfit)
    return outfit


@router.get("/history", response_model=List[OutfitResponse])
def list_outfit_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    outfits = (
        db.query(Outfit)
        .filter(Outfit.user_id == current_user.id)
        .order_by(Outfit.created_at.desc())
        .all()
    )
    return outfits

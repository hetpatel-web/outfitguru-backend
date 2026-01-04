from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import PreferencesResponse, PreferencesUpdate, UserResponse
from app.utils.deps import get_current_user, get_db

router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)


@router.patch("/me/preferences", response_model=PreferencesResponse)
def update_preferences(
    preferences: PreferencesUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    existing = dict(current_user.preferences or {})
    if preferences.goal is None:
        existing.pop("goal", None)
    else:
        existing["goal"] = preferences.goal
    current_user.preferences = existing
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return PreferencesResponse.model_validate(current_user.preferences or {})

from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.user import UserResponse
from app.utils.deps import get_current_user

router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)

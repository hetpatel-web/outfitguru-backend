from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import AuthRequest, AuthResponse, Token
from app.schemas.user import UserResponse
from app.utils.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(auth_request: AuthRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == auth_request.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    user = User(email=auth_request.email, password_hash=get_password_hash(auth_request.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = Token(access_token=create_access_token(user.id))
    return AuthResponse(user=UserResponse.from_orm(user), token=token)


@router.post("/login", response_model=Token)
def login(auth_request: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == auth_request.email).first()
    if not user or not verify_password(auth_request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password. Please try again."
        )
    return Token(access_token=create_access_token(user.id))

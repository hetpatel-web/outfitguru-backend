from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserResponse


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class AuthResponse(BaseModel):
    user: UserResponse
    token: Token


class PreferencesUpdate(BaseModel):
    preferences: Optional[Dict[str, Any]] = None

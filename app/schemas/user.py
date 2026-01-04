from datetime import datetime
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


GoalPreference = Literal["daily", "plan_ahead"]

class PreferencesUpdate(BaseModel):
    goal: Optional[GoalPreference] = Field(default=None)


class PreferencesResponse(PreferencesUpdate):
    model_config = ConfigDict(extra="allow")


class UserBase(BaseModel):
    email: EmailStr
    preferences: Optional[Dict[str, Any]] = Field(default=None)


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

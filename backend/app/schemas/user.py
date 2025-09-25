from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    role: Optional[UserRole] = UserRole.STUDENT
    jlpt_level: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email_or_username: str
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    jlpt_level: Optional[str] = None
    learning_preferences: Optional[str] = None
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    study_streak: int = 0
    total_study_time: int = 0
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None

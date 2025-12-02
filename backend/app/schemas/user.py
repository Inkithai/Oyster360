from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    FARM_MANAGER = "FARM_MANAGER"
    WORKER = "WORKER"

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole = UserRole.WORKER

class UserCreate(UserBase):
    password: str
    farm_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
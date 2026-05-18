from pydantic import BaseModel
from pydantic import EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    password: str
    confirm_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserLogout(BaseModel):
    id: int
    username: str
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True 

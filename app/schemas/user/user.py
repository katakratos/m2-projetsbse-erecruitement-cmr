from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(UserCreate):
    id: int
    email: str
    password: Optional[str] = None

    class Config:
        orm_mode = True    

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserUpdate(BaseModel):
    password: str
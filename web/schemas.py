from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    name: str
    password: str
    chat_id: int


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenRefresh(BaseModel):
    refresh_token: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class UserOut(BaseModel):
    id: int
    name: str
    telegram_id: int
    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    name: str
    password: str
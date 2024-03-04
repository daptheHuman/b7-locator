import datetime
from typing import Optional

from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class DataToken(BaseModel):
    id: Optional[int] = None


class UserOutput(BaseModel):
    id: Optional[int] = None
    username: str
    is_admin: bool
    created_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

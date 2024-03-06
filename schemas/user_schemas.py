from typing import Optional

from pydantic import BaseModel, Field


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None)
    password: Optional[str] = Field(None)
    is_admin: Optional[bool] = Field(None)

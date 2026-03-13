from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List

from schemas.entry_schema import EntrySchema


class UserAddSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserSchema(UserAddSchema):
    id: int
    entries: List[EntrySchema]

    model_config = ConfigDict(from_attributes=True)


class UserLoginSchema(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class RefreshData(BaseModel):
    token: str

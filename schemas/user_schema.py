from pydantic import BaseModel, EmailStr
from datetime import datetime
from pydantic import Field
from typing import List

from schemas.entry_schema import EntrySchema


class UserAddSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserSchema(UserAddSchema):
    id: int
    entries: List[EntrySchema]

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

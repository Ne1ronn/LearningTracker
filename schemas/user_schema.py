from pydantic import BaseModel, EmailStr
from datetime import datetime
from pydantic import Field
from typing import List

class UserAddSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserSchema(UserAddSchema):
    id: int

class Token(BaseModel):
    access_token: str
    token_type: str
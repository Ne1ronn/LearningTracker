from pydantic import BaseModel
from datetime import datetime
from typing import List
from pydantic.v1 import Field

class TopicAddSchema(BaseModel):
    title: str
    skill: str
    is_active: bool

class TopicSchema(TopicAddSchema):
    id: int

    class Config:
        from_attributes = True

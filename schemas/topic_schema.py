from pydantic import BaseModel
from datetime import datetime
from typing import List
from pydantic.v1 import Field

class TopicAddSchema(BaseModel):
    title: str
    skill: str
    need: int = Field(ge=1, le=10)
    progress_score: int = Field(ge=1, le=10)
    is_active: bool

class TopicSchema(TopicAddSchema):
    id: int

    class Config:
        from_attributes = True

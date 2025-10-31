from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from pydantic.v1 import Field

class TopicAddSchema(BaseModel):
    title: str
    skill: str
    need: int = Field(ge=1, le=10)
    progress_score: int = Field(ge=1, le=10)
    is_active: Optional[bool] = True

class UpdateTopicSchema(BaseModel):
    title: Optional[str]
    skill: Optional[str]
    need: Optional[int] = Field(ge=1, le=10)
    progress_score: Optional[int] = Field(ge=1, le=10)
    is_active: Optional[bool] = True

class TopicSchema(TopicAddSchema):
    id: int

    class Config:
        from_attributes = True

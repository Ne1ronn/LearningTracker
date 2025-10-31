from pydantic import BaseModel
from typing import List, Optional
from pydantic.v1 import Field

class TopicAddSchema(BaseModel):
    title: str
    skill: str
    need: int = Field(ge=1, le=10)
    progress_score: int = Field(ge=1, le=10)
    is_active: Optional[bool] = True

class UpdateTopicSchema(BaseModel):
    title: Optional[str] = None
    skill: Optional[str] = None
    need: Optional[int] = Field(default=None, ge=1, le=10)
    progress_score: Optional[int] = Field(default=None, ge=1, le=10)
    is_active: Optional[bool] = True

class TopicSchema(TopicAddSchema):
    id: int

    class Config:
        from_attributes = True

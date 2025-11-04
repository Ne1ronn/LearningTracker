from pydantic import BaseModel
from typing import List, Optional
from pydantic.v1 import Field

class TopicAddSchema(BaseModel):
    title: str
    skill: str
    need: int = Field(ge=1, le=10)
    progress_score: int = Field(ge=1, le=10)
    is_active: bool | None = True

class UpdateTopicSchema(BaseModel):
    title: str | None = None
    skill: str | None = None
    need: int | None = Field(default=None, ge=1, le=10)
    progress_score: int | None = Field(default=None, ge=1, le=10)
    is_active: bool | None = True

class TopicSchema(TopicAddSchema):
    id: int

    class Config:
        from_attributes = True

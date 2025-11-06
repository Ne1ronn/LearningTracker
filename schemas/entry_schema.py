from pydantic import BaseModel
from datetime import datetime
from pydantic import Field
from typing import List, Optional

from schemas.topic_schema import TopicSchema


class EntryAddSchema(BaseModel):
    username: str
    title: str
    description: str
    tags: str
    mood_score: int = Field(ge=1, le=10)
    progress_score: int = Field(ge=1, le=10)
    learning_hours: float
    topic_ids: List[int] | None = []

class UpdateEntrySchema(BaseModel):
    username: str | None = None
    title: str | None = None
    description: str | None = None
    tags: str | None = None
    mood_score: int | None = Field(default=None, ge=1, le=10)
    progress_score: int | None = Field(default=None, ge=1, le=10)
    learning_hours: int | None = None
    topic_ids: List[int] | None =  []

class EntrySchema(EntryAddSchema):
    id: int
    created_at: datetime
    topics: List[TopicSchema]

    class Config:
        from_attributes = True
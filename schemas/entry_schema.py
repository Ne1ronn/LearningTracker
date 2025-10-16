from pydantic import BaseModel
from datetime import datetime
from pydantic import Field
from typing import List, Optional

from schemas.topic_schema import TopicSchema


class EntryAddSchema(BaseModel):
    title: str
    description: str
    tags: str
    mood_score: int = Field(ge=1, le=10)
    topic_ids: Optional[List[int]] = []

class EntrySchema(EntryAddSchema):
    id: int
    created_at: datetime
    topics: List[TopicSchema]

    class Config:
        from_attributes = True
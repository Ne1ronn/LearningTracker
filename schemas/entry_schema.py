from pydantic import BaseModel
from datetime import datetime
from pydantic.v1 import Field


class EntryAddSchema(BaseModel):
    title: str
    topic: str
    description: str
    tags: str
    created_at: datetime
    mood_score: int = Field(ge=1, le=10)

class EntrySchema(EntryAddSchema):
    id: int
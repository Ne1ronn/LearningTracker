from pydantic import BaseModel
from datetime import datetime


class EntryAddSchema(BaseModel):
    title: str
    description: str
    tags: str
    created_at: datetime
    mood_score: int

class EntrySchema(EntryAddSchema):
    id: int
from pydantic import BaseModel
from datetime import datetime
from pydantic import Field
from typing import List, Optional

from schemas.topic_schema import TopicSchema

class TelegramTokenAddSchema(BaseModel):
    user_id: int
    telegram_id: int
    access_token: str

class TelegramTokenSchema(TelegramTokenAddSchema):
    id: int
    created_at: datetime
from pydantic import BaseModel
from datetime import datetime

class TelegramTokenAddSchema(BaseModel):
    user_id: int
    telegram_id: int
    access_token: str

class TelegramTokenSchema(TelegramTokenAddSchema):
    id: int
    created_at: datetime
from pydantic import BaseModel


class ProfileStatsResponseSchema(BaseModel):
    total_hours_all_time: float
    average_day_hours: float
    favorite_topic: str | None
    favorite_topic_hours: float
    current_streak: int
    max_streak: int

from pydantic import BaseModel


class WeeklyStatsResponseSchema(BaseModel):
    last_7_days_hours: float
    previous_7_days_hours: float
    delta_percent: float | None
    current_streak: int

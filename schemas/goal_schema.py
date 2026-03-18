from datetime import date
from pydantic import BaseModel, ConfigDict


class GoalAddSchema(BaseModel):
    topic_id: int
    target_hours: float
    target_date: date


class GoalUpdateSchema(BaseModel):
    topic_id: int | None = None
    target_hours: float | None = None
    target_date: date | None = None


class GoalResponseSchema(GoalAddSchema):
    id: int
    model_config = ConfigDict(from_attributes=True)

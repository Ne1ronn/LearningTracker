from pydantic import BaseModel

class TopicAddSchema(BaseModel):
    title: str
    skill: str
    description: str
    category: str
    is_active: bool | None = True

class UpdateTopicSchema(BaseModel):
    title: str | None = None
    skill: str | None = None
    description: str | None = None
    category: str | None = None
    is_active: bool | None = True

class TopicSchema(TopicAddSchema):
    id: int

    class Config:
        from_attributes = True

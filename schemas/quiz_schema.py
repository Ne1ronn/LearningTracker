from pydantic import BaseModel, ConfigDict


class QuizAddSchema(BaseModel):
    entry_id: int
    question: str
    answer: str


class QuizUpdateSchema(BaseModel):
    question: str | None = None
    answer: str | None = None


class QuizResponseSchema(QuizAddSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)

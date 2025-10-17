from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey
from datetime import datetime
from models.base import Base
from typing import List
from models.entry_topics_model import entry_topics


class EntryModel(Base):
    __tablename__ = "entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    tags: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    mood_score: Mapped[int]
    progress_score: Mapped[int]
    learning_hours: Mapped[float]

    topics: Mapped[List["TopicModel"]] = relationship("TopicModel", secondary=entry_topics, back_populates="entries")
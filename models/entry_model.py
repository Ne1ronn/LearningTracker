from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey
from datetime import datetime, UTC, tzinfo
from models.base import Base
from typing import List
from models.entry_topics_model import entry_topics


class EntryModel(Base):
    __tablename__ = "entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str]
    description: Mapped[str]
    tags: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    mood_score: Mapped[int]
    progress_score: Mapped[int]
    learning_hours: Mapped[float]
    private: Mapped[bool] = mapped_column(default=False)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="entries")
    topics: Mapped[List["TopicModel"]] = relationship("TopicModel", secondary=entry_topics, back_populates="entries")
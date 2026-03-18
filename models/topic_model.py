from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from typing import List
from models.entry_topics_model import entry_topics


class TopicModel(Base):
    __tablename__ = "topics"
    __table_args__ = (UniqueConstraint("user_id", "title"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str]
    description: Mapped[str]
    category: Mapped[str]
    skill: Mapped[str]
    is_active: Mapped[bool] = mapped_column(nullable=True, default=True)

    entries: Mapped[List["EntryModel"]] = relationship(
        "EntryModel", secondary=entry_topics, back_populates="topics"
    )
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="topics")
    goal: Mapped["GoalModel"] = relationship("GoalModel", back_populates="topic")

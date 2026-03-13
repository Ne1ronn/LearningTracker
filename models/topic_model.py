from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from typing import List
from models.entry_topics_model import entry_topics


class TopicModel(Base):
    __tablename__ = "topics"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    category: Mapped[str]
    skill: Mapped[str]
    is_active: Mapped[bool] = mapped_column(nullable=True, default=True)

    entries: Mapped[List["EntryModel"]] = relationship(
        "EntryModel", secondary=entry_topics, back_populates="topics"
    )

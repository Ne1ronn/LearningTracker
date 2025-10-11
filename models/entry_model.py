from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime
from datetime import datetime
from base import Base


class EntryModel(Base):
    __tablename__ = "entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    tags: Mapped[str]
    created_at: Mapped[DateTime] = mapped_column(default=datetime.utcnow)
    mood_score: Mapped[int]
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime
from datetime import date, datetime, UTC
from models.base import Base


class GoalModel(Base):
    __tablename__ = "goals"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), unique=True
    )
    started_at: Mapped[date] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None)
    )
    target_hours: Mapped[float]
    target_date: Mapped[date]

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="goals")
    topic: Mapped["TopicModel"] = relationship("TopicModel", back_populates="goal")

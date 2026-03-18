from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from typing import List


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    role: Mapped[str] = mapped_column(nullable=False, default="user")

    entries: Mapped[List["EntryModel"]] = relationship(
        "EntryModel", back_populates="user"
    )
    topics: Mapped[List["TopicModel"]] = relationship(
        "TopicModel", back_populates="user"
    )
    goals: Mapped[List["GoalModel"]] = relationship("GoalModel", back_populates="user")
    telegram_token: Mapped["TelegramTokenModel"] = relationship(
        "TelegramTokenModel", back_populates="user"
    )
    daily_stats: Mapped[List["DailyStatsModel"]] = relationship(
        "DailyStatsModel", back_populates="user"
    )

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import Date, ForeignKey, Column, Integer, Float
from models.base import Base
from typing import List


class DailyStatsModel(Base):
    __tablename__ = "daily_stats"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    date = Column(Date, primary_key=True)
    total_hours = Column(Float, nullable=False, default=0)
    entries_count = Column(Integer, nullable=False, default=0)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="daily_stats")

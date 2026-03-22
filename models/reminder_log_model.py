from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from datetime import datetime, date
from models.base import Base


class ReminderLogModel(Base):
    __tablename__ = "reminder_logs"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    reminder_type: Mapped[str] = mapped_column(primary_key=True)
    local_date: Mapped[date] = mapped_column(nullable=False, primary_key=True)
    sent_at: Mapped[datetime] = mapped_column(nullable=False)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="reminders")

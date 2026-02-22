from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from datetime import datetime
from models.base import Base


class TelegramTokenModel(Base):
    __tablename__ = "telegram_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    telegram_id: Mapped[int] = mapped_column(nullable=False, index=True)
    access_token: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="telegram_token")
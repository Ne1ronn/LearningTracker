from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from models.base import Base

class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    jti = Column(String, primary_key=True, index=True)
    user_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
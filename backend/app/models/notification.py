from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from .base import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    type = Column(String)  # email, in_app, push
    category = Column(String)  # system, billing, team, ai, harvest
    title = Column(String)
    message = Column(String)
    data = Column(JSON)  # Additional data
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime)
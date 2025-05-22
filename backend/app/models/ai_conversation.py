from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from .base import Base

class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
    messages = Column(JSON)  # List of {role, content}
    created_at = Column(DateTime)
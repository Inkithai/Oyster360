from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from .base import Base

class EnvironmentLog(Base):
    __tablename__ = "environment_logs"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    temperature = Column(Float)
    humidity = Column(Float)
    co2 = Column(Float)
    recorded_at = Column(DateTime)
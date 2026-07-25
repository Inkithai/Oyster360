from sqlalchemy import Column, Integer, String, ForeignKey, Float
from .base import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    name = Column(String, nullable=False)
    capacity = Column(Integer)
    temperature_target = Column(Float)
    humidity_target = Column(Float)
from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base

class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    sensor_type = Column(String)
    device_id = Column(String)
    status = Column(String, default="active")
    last_reading = Column(String)
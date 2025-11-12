from sqlalchemy import Column, Integer, String
from .base import Base

class Strain(Base):
    __tablename__ = "strains"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    species = Column(String, nullable=False)
    supplier = Column(String)
    colonization_days = Column(Integer)
    fruiting_days = Column(Integer)
    difficulty = Column(String)  # Easy, Medium, Hard
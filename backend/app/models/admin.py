from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from .base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    action = Column(String)  # create, update, delete, login, etc.
    resource = Column(String)  # user, batch, organization, etc.
    resource_id = Column(Integer)
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String)
    created_at = Column(DateTime)


class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    enabled = Column(Boolean, default=False)
    description = Column(String)
    config = Column(JSON)
    updated_at = Column(DateTime)
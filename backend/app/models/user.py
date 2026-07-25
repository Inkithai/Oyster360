from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, ForeignKey
import enum
from .base import Base

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    FARM_MANAGER = "FARM_MANAGER"
    WORKER = "WORKER"
    VIEWER = "VIEWER"  # Read-only access

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.WORKER)
    
    # Email verification
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True)
    email_verification_expires = Column(DateTime, nullable=True)
    
    # Profile
    avatar_url = Column(String, nullable=True)
    
    # Current organization
    current_organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # MFA
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String, nullable=True)
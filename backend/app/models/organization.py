from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Relationships
    members = relationship("OrganizationMember", back_populates="organization")
    farms = relationship("Farm", back_populates="organization")
    subscription = relationship("Subscription", back_populates="organization", uselist=False)


class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, default="MEMBER")  # OWNER, ADMIN, MANAGER, MEMBER, VIEWER
    joined_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

    organization = relationship("Organization", back_populates="members")
    user = relationship("User")
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from .base import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    stripe_customer_id = Column(String, index=True)
    stripe_subscription_id = Column(String, unique=True, index=True)
    plan = Column(String)  # free, starter, pro, enterprise
    status = Column(String)  # active, trialing, past_due, canceled, incomplete
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    trial_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    metadata = Column(JSON)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    organization = relationship("Organization", back_populates="subscription")
"""
Feature Gating based on Subscription
"""
from fastapi import HTTPException, Depends
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.subscription import Subscription
from app.database.database import get_db
from sqlalchemy.orm import Session

def require_subscription(plan: str = "pro"):
    """
    Decorator to require minimum subscription plan
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            db = kwargs.get("db")
            if not db:
                raise HTTPException(status_code=500, detail="Database not available")
            
            # Check subscription
            subscription = db.query(Subscription).filter(
                Subscription.organization_id == current_user.current_organization_id,
                Subscription.status.in_(["active", "trialing"])
            ).first()
            
            if not subscription:
                raise HTTPException(
                    status_code=403, 
                    detail="Active subscription required"
                )
            
            # Check plan level
            plan_levels = {"free": 0, "starter": 1, "pro": 2, "enterprise": 3}
            user_plan_level = plan_levels.get(subscription.plan, 0)
            required_level = plan_levels.get(plan, 2)
            
            if user_plan_level < required_level:
                raise HTTPException(
                    status_code=403,
                    detail=f"This feature requires {plan} plan or higher"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def check_feature_access(organization_id: int, feature: str, db: Session) -> bool:
    """Check if organization has access to a feature"""
    subscription = db.query(Subscription).filter(
        Subscription.organization_id == organization_id,
        Subscription.status.in_(["active", "trialing"])
    ).first()
    
    if not subscription:
        return False
    
    # Define feature access by plan
    feature_access = {
        "free": ["basic_batches", "basic_analytics"],
        "starter": ["basic_batches", "basic_analytics", "ai_assistant", "image_analysis"],
        "pro": ["basic_batches", "basic_analytics", "ai_assistant", "image_analysis", 
                "unlimited_batches", "advanced_analytics", "team_management"],
        "enterprise": ["all"]
    }
    
    user_features = feature_access.get(subscription.plan, [])
    return feature in user_features or "all" in user_features
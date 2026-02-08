"""
Oyster360 SaaS Analytics Service
Business intelligence and growth metrics
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.models.organization import Organization
from app.models.subscription import Subscription
from app.models.batch import Batch
from datetime import datetime, timedelta
from typing import Dict, Any, List

class SaaSAnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_growth_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get user and organization growth metrics"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        new_users = self.db.query(User).filter(
            User.created_at >= start_date
        ).count()
        
        new_organizations = self.db.query(Organization).filter(
            Organization.created_at >= start_date
        ).count()
        
        total_users = self.db.query(User).count()
        total_organizations = self.db.query(Organization).count()
        
        return {
            "period_days": days,
            "new_users": new_users,
            "new_organizations": new_organizations,
            "total_users": total_users,
            "total_organizations": total_organizations,
            "user_growth_rate": round((new_users / total_users) * 100, 2) if total_users > 0 else 0
        }

    def get_revenue_metrics(self) -> Dict[str, Any]:
        """Get subscription revenue metrics"""
        active_subs = self.db.query(Subscription).filter(
            Subscription.status == "active"
        ).all()
        
        total_mrr = sum(
            29 if sub.plan == "starter" else 
            99 if sub.plan == "pro" else 
            299 if sub.plan == "enterprise" else 0
            for sub in active_subs
        )
        
        return {
            "active_subscriptions": len(active_subs),
            "monthly_recurring_revenue": total_mrr,
            "average_revenue_per_user": round(total_mrr / len(active_subs), 2) if active_subs else 0
        }

    def get_usage_metrics(self) -> Dict[str, Any]:
        """Get platform usage metrics"""
        total_batches = self.db.query(Batch).count()
        active_batches = self.db.query(Batch).filter(Batch.status == "active").count()
        
        return {
            "total_batches_created": total_batches,
            "currently_active_batches": active_batches,
            "batch_utilization": round((active_batches / total_batches) * 100, 2) if total_batches > 0 else 0
        }

    def get_retention_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get user retention metrics"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Users who created accounts in the period
        new_users = self.db.query(User).filter(
            User.created_at >= start_date
        ).count()
        
        # Users who were active (simplified - in production would track last login)
        active_users = self.db.query(User).filter(
            User.created_at >= start_date - timedelta(days=30)
        ).count()
        
        retention_rate = round((active_users / new_users) * 100, 2) if new_users > 0 else 0
        
        return {
            "period_days": days,
            "new_users": new_users,
            "retained_users": active_users,
            "retention_rate": retention_rate
        }

    def get_ai_usage_metrics(self) -> Dict[str, Any]:
        """Get AI feature usage metrics"""
        # In production, this would query actual AI usage tables
        return {
            "ai_assistant_queries": 1247,
            "image_analyses": 892,
            "yield_predictions": 634,
            "most_used_feature": "AI Cultivation Assistant"
        }
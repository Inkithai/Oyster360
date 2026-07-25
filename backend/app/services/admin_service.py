"""
Oyster360 Admin Service
Administrative operations for SaaS management
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.organization import Organization
from app.models.subscription import Subscription
from app.models.admin import AuditLog, FeatureFlag
from datetime import datetime
from typing import List, Dict, Any

class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        total_users = self.db.query(User).count()
        total_organizations = self.db.query(Organization).count()
        total_subscriptions = self.db.query(Subscription).count()
        active_subscriptions = self.db.query(Subscription).filter(
            Subscription.status == "active"
        ).count()
        
        return {
            "total_users": total_users,
            "total_organizations": total_organizations,
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": active_subscriptions,
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_all_users(self, limit: int = 100) -> List[User]:
        """Get all users (admin only)"""
        return self.db.query(User).limit(limit).all()

    def get_all_organizations(self, limit: int = 100) -> List[Organization]:
        """Get all organizations (admin only)"""
        return self.db.query(Organization).limit(limit).all()

    def toggle_feature_flag(self, flag_name: str, enabled: bool) -> FeatureFlag:
        """Enable/disable a feature flag"""
        flag = self.db.query(FeatureFlag).filter(
            FeatureFlag.name == flag_name
        ).first()
        
        if not flag:
            flag = FeatureFlag(
                name=flag_name,
                enabled=enabled,
                updated_at=datetime.utcnow()
            )
            self.db.add(flag)
        else:
            flag.enabled = enabled
            flag.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(flag)
        return flag

    def log_action(
        self,
        user_id: int,
        action: str,
        resource: str,
        resource_id: int = None,
        old_values: dict = None,
        new_values: dict = None,
        ip_address: str = None
    ) -> AuditLog:
        """Log an administrative action"""
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            created_at=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()
        return log

    def get_audit_logs(self, limit: int = 100) -> List[AuditLog]:
        """Get recent audit logs"""
        return self.db.query(AuditLog).order_by(
            AuditLog.created_at.desc()
        ).limit(limit).all()
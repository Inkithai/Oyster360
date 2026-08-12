"""
Oyster360 User Onboarding Service
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from datetime import datetime

class OnboardingService:
    def __init__(self, db: Session):
        self.db = db

    def get_onboarding_status(self, user_id: int) -> dict:
        """Check user's onboarding progress"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"completed": False, "step": 0}
        
        org = self.db.query(Organization).filter(
            Organization.owner_id == user_id
        ).first()
        
        if not org:
            return {
                "completed": False,
                "step": 1,
                "message": "Create your first organization"
            }
        
        member_count = self.db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == org.id
        ).count()
        
        if member_count < 2:
            return {
                "completed": False,
                "step": 2,
                "message": "Invite your first team member"
            }
        
        return {"completed": True, "step": 3, "message": "Onboarding complete!"}
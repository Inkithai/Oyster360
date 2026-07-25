"""
Oyster360 Compliance API
GDPR and data protection endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.models.batch import Batch
from app.models.harvest import Harvest
from datetime import datetime
import json

router = APIRouter()

@router.get("/export-data")
def export_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GDPR Article 15 - Right to Access
    Export all user data in machine-readable format
    """
    # Collect all user data
    user_data = {
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None
        },
        "organizations": [],
        "batches": [],
        "harvests": []
    }
    
    # Get organizations
    members = db.query(OrganizationMember).filter(
        OrganizationMember.user_id == current_user.id
    ).all()
    
    for member in members:
        org = db.query(Organization).filter(Organization.id == member.organization_id).first()
        if org:
            user_data["organizations"].append({
                "id": org.id,
                "name": org.name,
                "role": member.role,
                "joined_at": member.joined_at.isoformat() if member.joined_at else None
            })
    
    # Get batches (simplified - in production would include all related data)
    batches = db.query(Batch).filter(
        Batch.organization_id.in_([m.organization_id for m in members])
    ).all()
    
    for batch in batches:
        user_data["batches"].append({
            "id": batch.id,
            "batch_number": batch.batch_number,
            "organization_id": batch.organization_id,
            "status": batch.status,
            "created_at": batch.created_at.isoformat() if batch.created_at else None
        })
    
    # Get harvests
    harvests = db.query(Harvest).filter(
        Harvest.organization_id.in_([m.organization_id for m in members])
    ).all()
    
    for harvest in harvests:
        user_data["harvests"].append({
            "id": harvest.id,
            "batch_id": harvest.batch_id,
            "quantity_kg": harvest.quantity_kg,
            "quality_score": harvest.quality_score,
            "harvest_date": harvest.harvest_date.isoformat() if harvest.harvest_date else None
        })
    
    return {
        "export_date": datetime.utcnow().isoformat(),
        "data": user_data
    }

@router.delete("/delete-data")
def delete_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GDPR Article 17 - Right to be Forgotten
    Anonymize or delete user data
    """
    # Anonymize user data
    current_user.name = "[Deleted User]"
    current_user.email = f"deleted_{current_user.id}@example.com"
    current_user.password_hash = ""
    current_user.avatar_url = None
    current_user.mfa_secret = None
    
    # Remove from organizations
    db.query(OrganizationMember).filter(
        OrganizationMember.user_id == current_user.id
    ).delete()
    
    db.commit()
    
    return {"message": "Data deletion completed"}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.organization import Organization, OrganizationMember
from app.models.user import User
from app.core.dependencies import get_current_user, manager_only
from pydantic import BaseModel
from datetime import datetime
import secrets

router = APIRouter()

class OrganizationCreate(BaseModel):
    name: str
    slug: str

class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str
    is_active: bool

@router.post("/", response_model=OrganizationResponse)
def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if slug already exists
    existing = db.query(Organization).filter(Organization.slug == org_data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Organization slug already taken")
    
    # Create organization
    organization = Organization(
        name=org_data.name,
        slug=org_data.slug,
        owner_id=current_user.id,
        created_at=datetime.utcnow()
    )
    db.add(organization)
    db.flush()
    
    # Add user as owner
    member = OrganizationMember(
        organization_id=organization.id,
        user_id=current_user.id,
        role="OWNER",
        joined_at=datetime.utcnow()
    )
    db.add(member)
    
    # Set as current organization
    current_user.current_organization_id = organization.id
    
    db.commit()
    db.refresh(organization)
    
    return organization

@router.get("/my-organizations")
def get_user_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    members = db.query(OrganizationMember).filter(
        OrganizationMember.user_id == current_user.id,
        OrganizationMember.is_active == True
    ).all()
    
    organizations = []
    for member in members:
        org = db.query(Organization).filter(Organization.id == member.organization_id).first()
        if org:
            organizations.append({
                "id": org.id,
                "name": org.name,
                "slug": org.slug,
                "role": member.role,
                "is_current": org.id == current_user.current_organization_id
            })
    
    return organizations

@router.post("/switch/{organization_id}")
def switch_organization(
    organization_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify membership
    member = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == organization_id,
        OrganizationMember.user_id == current_user.id,
        OrganizationMember.is_active == True
    ).first()
    
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    current_user.current_organization_id = organization_id
    db.commit()
    
    return {"message": "Organization switched successfully"}
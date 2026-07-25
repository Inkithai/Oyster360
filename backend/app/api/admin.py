from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.admin_service import AdminService
from app.core.dependencies import admin_only
from app.models.admin import FeatureFlag
from app.models.user import User

router = APIRouter()

@router.get("/stats")
def get_system_stats(
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    service = AdminService(db)
    return service.get_system_stats()

@router.get("/users")
def get_all_users(
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    service = AdminService(db)
    users = service.get_all_users()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "email_verified": u.email_verified
        } for u in users
    ]

@router.get("/organizations")
def get_all_organizations(
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    service = AdminService(db)
    orgs = service.get_all_organizations()
    return [
        {
            "id": o.id,
            "name": o.name,
            "slug": o.slug,
            "is_active": o.is_active
        } for o in orgs
    ]

@router.get("/audit-logs")
def get_audit_logs(
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    service = AdminService(db)
    logs = service.get_audit_logs()
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "resource": log.resource,
            "created_at": log.created_at
        } for log in logs
    ]

@router.get("/feature-flags")
def get_feature_flags(
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    service = AdminService(db)
    flags = db.query(FeatureFlag).all()
    return [
        {
            "name": flag.name,
            "enabled": flag.enabled,
            "description": flag.description
        } for flag in flags
    ]

@router.post("/feature-flags/{flag_name}")
def toggle_feature_flag(
    flag_name: str,
    enabled: bool,
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    service = AdminService(db)
    flag = service.toggle_feature_flag(flag_name, enabled)
    return {"name": flag.name, "enabled": flag.enabled}
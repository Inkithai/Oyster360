from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.saas_analytics_service import SaaSAnalyticsService
from app.core.dependencies import admin_only
from app.models.user import User

router = APIRouter()

@router.get("/growth")
def get_growth_metrics(
    days: int = 30,
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    service = SaaSAnalyticsService(db)
    return service.get_growth_metrics(days)

@router.get("/revenue")
def get_revenue_metrics(
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    service = SaaSAnalyticsService(db)
    return service.get_revenue_metrics()

@router.get("/usage")
def get_usage_metrics(
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    service = SaaSAnalyticsService(db)
    return service.get_usage_metrics()

@router.get("/retention")
def get_retention_metrics(
    days: int = 30,
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    service = SaaSAnalyticsService(db)
    return service.get_retention_metrics(days)

@router.get("/ai-usage")
def get_ai_usage_metrics(
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    service = SaaSAnalyticsService(db)
    return service.get_ai_usage_metrics()
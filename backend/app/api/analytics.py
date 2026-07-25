from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.analytics_service import AnalyticsService
from app.core.dependencies import manager_only
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()

class YieldPredictionRequest(BaseModel):
    batch_id: int

@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only)
):
    service = AnalyticsService(db)
    return service.get_dashboard_stats()

@router.post("/predict-yield")
def predict_yield(
    request: YieldPredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only)
):
    service = AnalyticsService(db)
    result = service.predict_yield_for_batch(request.batch_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/environment")
def get_environment_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only)
):
    service = AnalyticsService(db)
    return service.get_environment_trends()

@router.get("/strains")
def get_strain_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only)
):
    service = AnalyticsService(db)
    return service.get_strain_performance()

@router.get("/recipes")
def get_recipe_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only)
):
    service = AnalyticsService(db)
    return service.get_recipe_performance()
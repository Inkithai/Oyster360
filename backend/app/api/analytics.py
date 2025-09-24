from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import manager_only
from app.core.tenant import get_current_organization
from app.database.database import get_db
from app.models.user import User
from app.services.analytics_service import AnalyticsService

router = APIRouter()


class YieldPredictionRequest(BaseModel):
    batch_id: int


@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
    organization_id: int = Depends(get_current_organization),
):
    return AnalyticsService(db).get_dashboard_stats(organization_id)


@router.post("/predict-yield")
def predict_yield(
    request: YieldPredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
    organization_id: int = Depends(get_current_organization),
):
    result = AnalyticsService(db).predict_yield_for_batch(
        request.batch_id,
        organization_id,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/environment")
def get_environment_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
    organization_id: int = Depends(get_current_organization),
):
    return AnalyticsService(db).get_environment_trends(organization_id)


@router.get("/strains")
def get_strain_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
    organization_id: int = Depends(get_current_organization),
):
    return AnalyticsService(db).get_strain_performance(organization_id)


@router.get("/recipes")
def get_recipe_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
    organization_id: int = Depends(get_current_organization),
):
    return AnalyticsService(db).get_recipe_performance(organization_id)

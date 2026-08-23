from fastapi import FastAPI, Request, Depends, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.error_tracking import init_error_tracking
from app.core.logging import configure_logging, logger
from app.core.middleware import add_request_id, add_security_headers
from app.core.rate_limit import rate_limit_middleware
from app.core.tenant_middleware import TenantMiddleware
from app.database.database import get_db
from app.api import (
    auth_router, batches_router, recipes_router, 
    growth_logs_router, harvests_router, environment_router, 
    analytics_router, strains_router, rooms_router, ai_router, 
    inspections_router, assistant_router, inventory_router, purchases_router, harvest_grades_router,
    ai_assistant_router, organizations_router, billing_router, notifications_router, admin_router,
    saas_analytics_router, mfa_router, compliance_router, webhooks_router
)

configure_logging(settings.LOG_LEVEL)
init_error_tracking()

app = FastAPI(title="Oyster360", version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Tenant Middleware
app.add_middleware(TenantMiddleware)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled request error",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "method": request.method,
            "path": request.url.path,
        },
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )

@app.middleware("http")
async def _security_headers(request: Request, call_next):
    return await add_security_headers(request, call_next)


@app.middleware("http")
async def _request_id(request: Request, call_next):
    return await add_request_id(request, call_next)


@app.middleware("http")
async def _rate_limit(request: Request, call_next):
    return await rate_limit_middleware(request, call_next)

# Include all routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(batches_router, prefix="/api/batches", tags=["Batches"])
app.include_router(recipes_router, prefix="/api/recipes", tags=["Recipes"])
app.include_router(growth_logs_router, prefix="/api", tags=["Growth Logs"])
app.include_router(harvests_router, prefix="/api", tags=["Harvests"])
app.include_router(environment_router, prefix="/api", tags=["Environment"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(strains_router, prefix="/api/strains", tags=["Strains"])
app.include_router(rooms_router, prefix="/api/rooms", tags=["Rooms"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI"])
app.include_router(inspections_router, prefix="/api/inspections", tags=["Inspections"])
app.include_router(assistant_router, prefix="/api/assistant", tags=["AI Assistant"])
app.include_router(ai_assistant_router, prefix="/api/ai/assistant", tags=["AI Assistant"])
app.include_router(inventory_router, prefix="/api/inventory", tags=["Inventory"])
app.include_router(purchases_router, prefix="/api/purchases", tags=["Purchases"])
app.include_router(harvest_grades_router, prefix="/api/harvest-grades", tags=["Harvest Grading"])
app.include_router(organizations_router, prefix="/api/organizations", tags=["Organizations"])
app.include_router(billing_router, prefix="/api/billing", tags=["Billing"])
app.include_router(notifications_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(saas_analytics_router, prefix="/api/saas-analytics", tags=["SaaS Analytics"])
app.include_router(mfa_router, prefix="/api/mfa", tags=["MFA"])
app.include_router(compliance_router, prefix="/api/compliance", tags=["Compliance"])
app.include_router(webhooks_router, prefix="/api/webhooks", tags=["Webhooks"])

@app.get("/")
def root():
    return {"message": "MycoFarm AI - Oyster Mushroom Platform"}

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime


class ReadinessResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime


@app.get("/health", response_model=HealthResponse, tags=["Operations"])
def health_check():
    """Dependency-free process health check for load balancers."""
    return HealthResponse(
        status="healthy",
        service="oyster360-backend",
        timestamp=datetime.now(timezone.utc),
    )


@app.get("/ready", response_model=ReadinessResponse, tags=["Operations"])
def readiness_check(response: Response, db: Session = Depends(get_db)):
    """Report whether this instance can serve database-backed traffic."""
    try:
        db.execute(text("SELECT 1"))
        database_status = "connected"
        readiness_status = "ready"
    except Exception:
        logger.exception("Database readiness check failed")
        database_status = "unavailable"
        readiness_status = "not_ready"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        status=readiness_status,
        database=database_status,
        timestamp=datetime.now(timezone.utc),
    )


@app.get("/live", tags=["Operations"])
def liveness_check():
    """Liveness check for container orchestrators."""
    return {"status": "alive"}

@app.get("/celery-status")
def celery_status():
    """Check Celery worker status"""
    from app.core.celery import celery_app
    i = celery_app.control.inspect(timeout=1)
    return {
        "active_workers": i.active() if i else [],
        "scheduled_tasks": i.scheduled() if i else []
    }
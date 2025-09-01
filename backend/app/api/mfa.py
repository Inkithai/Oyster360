from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.mfa_service import MFAService
from app.core.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()

class VerifyTokenRequest(BaseModel):
    token: str

@router.post("/setup")
def setup_mfa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MFAService(db)
    return service.generate_secret(current_user.id)

@router.post("/verify")
def verify_mfa(
    request: VerifyTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MFAService(db)
    success = service.enable_mfa(current_user.id, request.token)
    return {"success": success}

@router.post("/disable")
def disable_mfa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MFAService(db)
    success = service.disable_mfa(current_user.id)
    return {"success": success}
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.notification_service import NotificationService
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/")
def get_notifications(
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    return service.get_user_notifications(current_user.id, unread_only)

@router.post("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    success = service.mark_as_read(notification_id, current_user.id)
    return {"success": success}
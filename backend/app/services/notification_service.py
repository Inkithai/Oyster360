"""
Oyster360 Notification Service
Handles email, in-app, and push notifications
"""
from sqlalchemy.orm import Session
from app.models.notification import Notification
from datetime import datetime
from typing import Dict, Any, Optional
import os

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        category: str = "system",
        notification_type: str = "in_app",
        organization_id: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Create an in-app notification"""
        notification = Notification(
            user_id=user_id,
            organization_id=organization_id,
            type=notification_type,
            category=category,
            title=title,
            message=message,
            data=data or {},
            created_at=datetime.utcnow()
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_user_notifications(self, user_id: int, unread_only: bool = False):
        """Get notifications for a user"""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
            
        return query.order_by(Notification.created_at.desc()).limit(50).all()

    def mark_as_read(self, notification_id: int, user_id: int):
        """Mark a notification as read"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            self.db.commit()
            return True
        return False

    def send_email_notification(self, user_email: str, subject: str, body: str):
        """Send email notification (placeholder for production email service)"""
        # In production, integrate with SendGrid, AWS SES, or similar
        print(f"[EMAIL] To: {user_email}, Subject: {subject}")
        return True

    def create_batch_notification(self, user_id: int, batch_number: str, message: str):
        """Create a batch-related notification"""
        return self.create_notification(
            user_id=user_id,
            title=f"Batch Update: {batch_number}",
            message=message,
            category="harvest"
        )
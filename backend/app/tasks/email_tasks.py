"""
Email Background Tasks
"""
from app.core.celery import celery_app
import time

@celery_app.task(name="send_email")
def send_email_task(to_email: str, subject: str, body: str):
    """
    Send email in background
    In production, integrate with SendGrid, AWS SES, or Mailgun
    """
    # Simulate email sending
    print(f"[EMAIL TASK] Sending to: {to_email}")
    print(f"[EMAIL TASK] Subject: {subject}")
    print(f"[EMAIL TASK] Body: {body[:100]}...")
    
    # In production:
    # sendgrid_client.send(...)
    # or
    # ses_client.send_email(...)
    
    return {"status": "sent", "to": to_email}

@celery_app.task(name="send_welcome_email")
def send_welcome_email(user_email: str, user_name: str):
    """Send welcome email to new users"""
    subject = "Welcome to Oyster360!"
    body = f"Hi {user_name}, thank you for joining Oyster360!"
    return send_email_task.delay(user_email, subject, body)
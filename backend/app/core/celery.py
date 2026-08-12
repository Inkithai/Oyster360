"""
Oyster360 Celery Configuration
Production-ready background job processing with Redis
"""
from celery import Celery
from celery.schedules import crontab
import os

# Redis URL for Celery broker and result backend
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "oyster360",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.ai_tasks",
        "app.tasks.maintenance_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,
    result_expires=3600,  # Results expire after 1 hour
    task_acks_late=True,  # Acknowledge tasks after completion
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
)

# Periodic tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    'cleanup-expired-tokens': {
        'task': 'app.tasks.maintenance_tasks.cleanup_expired_tokens',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
    'generate-daily-reports': {
        'task': 'app.tasks.maintenance_tasks.generate_daily_reports',
        'schedule': crontab(hour=6, minute=0),  # Run daily at 6 AM
    },
}
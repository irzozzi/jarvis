from celery import Celery
import os

# Redis используется как брокер и бэкенд (результаты)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "jarvis",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.insights", "app.tasks.notifications"]  # модули с задачами
)

# Настройки Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    beat_schedule={
        "generate-daily-insights": {
            "task": "app.tasks.insights.generate_daily_insights",
            "schedule": 86400.0,  # раз в сутки (24*60*60)
            "args": (),
        },
        "send-upcoming-event-notifications": {
            "task": "app.tasks.notifications.send_upcoming_event_notifications",
            "schedule": 600.0,  # каждые 10 минут
            "args": (),
        },
    },
)
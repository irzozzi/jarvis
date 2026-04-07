from celery import shared_task
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app import models
from app.services.email_service import send_event_reminder_email

@shared_task
def send_upcoming_event_notifications():
    print("=== Задача send_upcoming_event_notifications запущена ===")
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        soon = now + timedelta(minutes=30)
        events = db.query(models.Event).filter(
            models.Event.start_time >= now,
            models.Event.start_time <= soon,
            models.Event.status == "planned",
            models.Event.notification_sent == False
        ).all()
        print(f"Найдено событий: {len(events)}")
        for event in events:
            user = db.query(models.User).filter(models.User.id == event.user_id).first()
            if user and user.email:
                print(f"Отправка письма на {user.email} для события {event.title}")
                send_event_reminder_email(user.email, event.title, event.start_time)
                event.notification_sent = True
                db.commit()
            else:
                print(f"Пользователь {event.user_id} не найден или нет email")
    finally:
        db.close()
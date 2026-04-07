from celery import shared_task
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app import models 

@shared_task
def send_upcoming_event_notifications():
    print ("Функция вызвана")
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        soon = now + timedelta(minutes=30)
        events = db.query(models.Event).filter(
            models.Event.start_time >= now,
            models.Event.start_time <= soon,
            models.Event.status == "planned"
        ).all()
        for event in events:
            # Здесь можно добавить реальную отправку (email, push)
            print(f"[Celery] Напоминание: событие '{event.title}' начнется в {event.start_time}")
    finally:
        db.close()

from celery import shared_task
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app import models
from app.services import analytics

@shared_task
def generate_daily_insights():
    db = SessionLocal()
    try:
        users = db.query(models.User).filter(models.User.is_active == True).all()
        for user in users:
            analytics.generate_all_insights(db, str(user.id))
        db.commit()
    finally:
        db.close()
        

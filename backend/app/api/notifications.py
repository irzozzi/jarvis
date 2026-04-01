from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from .. import schemas, models
from ..api import deps

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/upcoming", response_model=List[schemas.EventOut])
def get_upcoming_events(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    minutes: int = 30,
):
    now = datetime.utcnow()
    soon = now + timedelta(minutes=minutes)
    # Отладочные выводы
    print(f"DEBUG: now = {now}, soon = {soon}")
    events = db.query(models.Event).filter(
        models.Event.user_id == current_user.id,
        models.Event.start_time >= now,
        models.Event.start_time <= soon
    ).order_by(models.Event.start_time).all()
    print(f"DEBUG: found events count = {len(events)}")
    for e in events:
        print(f"DEBUG: event: {e.id}, {e.title}, start={e.start_time}")
    return events
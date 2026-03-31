from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from .. import models

def create_event_from_request(
    db: Session,
    user_id: UUID,
    title: str, 
    start_time: datetime,
    end_time: datetime,
    description: str = None, 
    habit_id: UUID = None,
) -> models.Event:
    event = models.Event(
        user_id=user_id,
        habit_id=habit_id,
        title=title,
        description=description,
        start_time=start_time,
        end_time=end_time,
        status="planned"
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

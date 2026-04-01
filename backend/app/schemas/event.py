from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, Any

class EventBase(BaseModel):
    habit_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    recurrence: Optional[Any] = None
    status: Optional[str] = "planned"

class EventCreate(EventBase):
    @field_validator('start_time', 'end_time')
    def convert_to_utc(cls, v: datetime) -> datetime:
        # Если время наивное (без часового пояса), считаем его UTC
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        # Если есть часовой пояс, преобразуем в UTC
        return v.astimezone(timezone.utc).replace(tzinfo=None)

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    recurrence: Optional[Any] = None
    status: Optional[str] = None

class EventOut(EventBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
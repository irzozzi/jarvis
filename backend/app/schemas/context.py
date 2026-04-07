from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, Any

class ContextBase(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    activity: Optional[str] = None
    raw_data: Optional[Any] = None
    location_type: Optional[str] = None   # <-- добавить
    weather: Optional[Any] = None         # <-- добавить

class ContextCreate(ContextBase):
    timestamp: Optional[datetime] = None

class ContextOut(ContextBase):
    id: UUID
    user_id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
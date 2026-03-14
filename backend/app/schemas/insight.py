from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, Any

class InsightCreate(BaseModel):
    habit_id: Optional[UUID] = None
    type: str
    content: str
    data: Optional[Any] = None

class InsightOut(BaseModel):
    pass

class Insight(BaseModel):
    id: UUID
    user_id: UUID
    created_at: datetime
    is_read: bool

    model_config = ConfigDict(from_attributes=True)
    


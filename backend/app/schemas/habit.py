from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str
    target: float
    unit: Optional[str] = None
    schedule: Optional[dict] = None   # <-- заменили на dict

class HabitCreate(HabitBase):
    pass

class HabitOut(HabitBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
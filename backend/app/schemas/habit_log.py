from pydantic import BaseModel, ConfigDict
from uuid import UUID 
from datetime import datetime
from typing import Optional

class HabitLogBase(BaseModel):
    habit_id: UUID
    value: float 
    notes: Optional[str] = None
    mood: Optional[int] = None

class HabitLogCreate(HabitLogBase):
    pass

class HabitLogOut(HabitLogBase):
    id: UUID
    completed_at: datetime

    model_config = ConfigDict(from_attributes=True)

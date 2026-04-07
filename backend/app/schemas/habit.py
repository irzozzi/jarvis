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
    schedule: Optional[dict] = None

class HabitCreate(HabitBase):
    pass

class HabitOut(HabitBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

# Дополнительные схемы для логов привычек
class HabitLogCreate(BaseModel):
    value: float
    notes: Optional[str] = None
    mood: Optional[int] = None
    context_id: Optional[UUID] = None

class HabitLogOut(BaseModel):
    id: UUID
    habit_id: UUID
    value: float
    notes: Optional[str] = None
    mood: Optional[int] = None
    completed_at: datetime
    context_id: Optional[UUID] = None
    model_config = ConfigDict(from_attributes=True)
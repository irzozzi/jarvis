import re 
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class GoalCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class GoalCategoryCreate(GoalCategoryBase):
    pass

class GoalCategoryOut(GoalCategoryBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    target_date: Optional[datetime] = None
    custom_text: Optional[str] = None

class GoalCreate(GoalBase):
    pass

class GoalUpdate(GoalBase):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    target_date: Optional[datetime] = None
    status: Optional[str] = None
    progress: Optional[float] = None

class GoalOut(GoalBase):
    id: UUID
    user_id: UUID
    start_date: datetime
    progress: float
    status: str
    created_at: datetime
    updated_at: datetime

    habits: List[UUID] = []

    model_config = ConfigDict(from_attributes=True)
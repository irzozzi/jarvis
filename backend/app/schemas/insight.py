from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, Any

class InsightBase(BaseModel):
    habit_id: Optional[UUID] = None
    type: str
    content: str
    data: Optional[Any] = None

class InsightCreate(InsightBase):
    pass

class InsightOut(InsightBase):  # теперь наследует все поля из InsightBase
    id: UUID
    user_id: UUID
    created_at: datetime
    is_read: bool

    model_config = ConfigDict(from_attributes=True)
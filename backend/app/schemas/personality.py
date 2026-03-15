from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

class QuestionAnswer(BaseModel):
    question_id: int
    answer: int

class PersonalityCreate(BaseModel):
    answers: List[QuestionAnswer]

class PersonalityOut(BaseModel):
    id: UUID
    user_id: UUID
    type: Optional[str] = None
    answers: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


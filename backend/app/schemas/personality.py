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
    answers: Optional[List[Dict[str, Any]]] = None
    openness: Optional[float] = None
    conscientiousness: Optional[float] = None
    extraversion: Optional[float] = None
    agreeableness: Optional[float] = None
    neuroticism: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class QuestionOut(BaseModel):
    id: int
    text: str
    # factor и direction не обязательны для клиента, но можно вернуть и их, если нужно
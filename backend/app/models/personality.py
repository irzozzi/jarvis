from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..core.database import Base

class Personality(Base):
    __tablename__ = "personality"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    answers = Column(JSON, nullable=True)          # сохраняем ответы на вопросы (для истории)
    openness = Column(Float, nullable=True)       # 0..100
    conscientiousness = Column(Float, nullable=True)
    extraversion = Column(Float, nullable=True)
    agreeableness = Column(Float, nullable=True)
    neuroticism = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
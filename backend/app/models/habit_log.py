from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime 
from ..core.database import Base

class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    habit_id = Column(UUID(as_uuid=True), ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    value = Column(Float, nullable=False)
    notes = Column(String, nullable=True)
    mood = Column(Integer, nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
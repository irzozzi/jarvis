from sqlalchemy import Column, ForeignKey, UUID as SQLUUID, Float, String, Integer, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid

class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    habit_id = Column(SQLUUID(as_uuid=True), ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    value = Column(Float, nullable=False)
    notes = Column(String, nullable=True)
    mood = Column(Integer, nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow)
    context_id = Column(SQLUUID(as_uuid=True), ForeignKey("context.id", ondelete="SET NULL"), nullable=True)

    habit = relationship("Habit", back_populates="logs")
    context = relationship("Context", back_populates="habit_logs")
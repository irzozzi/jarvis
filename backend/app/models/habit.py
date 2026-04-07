from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from ..core.database import Base

# Импорт HabitLog не обязателен, так как используется строковое имя, но для type hint можно добавить
# from app.models.habit_log import HabitLog

class Habit(Base):
    __tablename__ = "habits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type = Column(String, nullable=False)
    target = Column(Float, nullable=False)
    unit = Column(String, nullable=True)

    schedule = Column(JSONB, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    deleted_at = Column(DateTime, nullable=True)

    # Отношение к логам привычки (добавить эту строку)
    logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")
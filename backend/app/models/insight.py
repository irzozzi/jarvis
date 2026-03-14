from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON, Float   
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..core.database import Base

class Insight(Base):
    __tablename__ = "insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    habit_id = Column(UUID(as_uuid=True), ForeignKey("habits.id", ondelete="CASCADE"), nullable=True)  # null для общих инсайтов
    type = Column(String, nullable=False)  # например: "time_pattern", "context_pattern", "keystone_habit"
    content = Column(String, nullable=False)  # текст инсайта
    data = Column(JSON, nullable=True)  # дополнительные данные (например, часы пик, корреляции)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)  # прочитал ли пользователь
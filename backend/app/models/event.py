from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..core.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    habit_id = Column(UUID(as_uuid=True), ForeignKey("habits.id", ondelete="SET NULL"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(DateTime, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    recurrence = Column(JSON, nullable=True)
    status = Column(String, default="planned")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notification_sent = Column(Boolean, default=False)

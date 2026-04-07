from sqlalchemy import Column, UUID as SQLUUID, Float, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid

class Context(Base):
    __tablename__ = "context"

    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(SQLUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_type = Column(String, nullable=True)
    weather = Column(JSON, nullable=True)
    activity = Column(String, nullable=True)
    raw_data = Column(JSON, nullable=True)

    # Связь с логами привычек
    habit_logs = relationship("HabitLog", back_populates="context")
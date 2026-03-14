from sqlalchemy import  Column, String, Float, Boolean, DateTime, ForeignKey, Integer 
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime
from ..core.database import Base

class Habit(Base):
    __tablename__ = "habits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type = Column(String, nullable=False)
    target = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
    shedule = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

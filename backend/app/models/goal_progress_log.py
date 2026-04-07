from sqlalchemy import Column, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..core.database import Base

class GoalProgressLog(Base):
    __tablename__ = "goal_progress_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    progress = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    

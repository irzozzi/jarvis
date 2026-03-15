from sqlalchemy import Column, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..core.database import Base

class Context(Base):
    __tablename__ ="context"

    id = Column(UUID(as_uuid=True), primary_key=True, defaul=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    latitude = Column(Float, nullable=True)
    longtude = Column(Float, nullable=True)
    location_type = Column(String, nullable=True)
    weather = Column(JSON, nullable=True)
    activity = Column(String, nullable=True)
    raw_data = Column(JSON, nullable=True)
    


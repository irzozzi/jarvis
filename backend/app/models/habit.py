from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey
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

    # Поле schedule может хранить различные форматы:
    # - {"days": [1,3,5], "time": "07:00"}        # старый формат (еженедельно по дням недели)
    # - {"type": "weekly", "days": [1,3,5]}       # новый формат для еженедельного
    # - {"type": "every_n_days", "interval": 2}   # каждые N дней
    # - {"type": "monthly", "day_of_month": 15}   # ежемесячно по числу
    # - {"type": "custom_dates", "dates": ["2026-04-01", "2026-04-10"]} # конкретные даты
    schedule = Column(JSONB, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    deleted_at = Column(DateTime, nullable=True)
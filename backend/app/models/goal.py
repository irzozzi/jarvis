from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Table, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..core.database import Base

goal_habits = Table(
    "goal_habits",
    Base.metadata,
    Column("goal_id", UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), primary_key=True),
    Column("habit_id", UUID(as_uuid=True), ForeignKey("habits.id", ondelete="CASCADE"), primary_key=True),
)

class GoalCategory(Base):
    __tablename__ = "goal_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

class Goal(Base):
    __tablename__ = "goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("goal_categories.id", ondelete="SET NULL"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    custom_text = Column(Text, nullable=True)
    start_date = Column(DateTime, default=datetime.utcnow)
    target_date = Column(DateTime, nullable=True)
    progress = Column(Float, default=0.0)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)



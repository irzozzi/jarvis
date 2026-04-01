from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class ChartPoint(BaseModel):
    date: date
    value: float

class HabitChartData(BaseModel):
    habit_id: Optional[str] = None
    habit_name: Optional[str] = None
    data: List[ChartPoint]

class GoalProgressData(BaseModel):
    goal_id: str
    goal_title: str
    data: List[ChartPoint]
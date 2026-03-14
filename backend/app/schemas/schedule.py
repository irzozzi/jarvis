from pydantic import BaseModel
from typing import Optional, List

class Schedule(BaseModel):
    days: Optional[List[int]] = None
    time: Optional[str] = None
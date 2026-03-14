from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID
from typing import List

from .. import schemas, models
from ..api import deps 

router = APIRouter(prefix="/habits", tags=["habits"])

@router.get("/", response_model=List[schemas.HabitOut])
def read_habits(
    db: Session = Depends(deps.get_db),
    current_user: models.user = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    habits = db.query(models.Habit).filter(
        models.Habit.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return habits

@router.post("/", response_model=schemas.HabitOut, status_code=status.HTTP_201_CREATED)
def create_habit(
    habit_in: schemas.HabitCreate, 
    db: Session = Depends(deps.get_db),
    current_user: models.user = Depends(deps.get_current_user),
):
    habit = models.Habit(
        **habit_in.model_dump(),
        user_id=current_user.id
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit 

@router.get("/{habit_id}", response_model=schemas.HabitOut)
def read_habit(
    habit_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    habit = db.query(models.Habit).filter(
        models.Habit.id == habit_id,
        models.Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
        return habit

@router.put("/{habit_id}", response_model=schemas.HabitOut)
def update_habit(
    habit_id: UUID,
    habit_in: schemas.HabitCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    habit = db.query(models.Habit).filter(
        models.Habit.id == habit_id,
        models.Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    for field, value in habit_in.model_dump().items():
        setattr(habit, field, value)

    db.commit()
    db.refresh(habit)
    return habit       

@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(
    habit_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    habit = db.query(models.Habit).filter(
        models.Habit.id == habit_id,
        models.Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habot not found")

    db.delete(habit)
    db.commit()
    return None

@router.post("/{habit_id}/logs", response_model=schemas.HabitLogOut, status_code=status.HTTP_201_CREATED)
def create_habit_log(
    habit_id: UUID,
    log_in: schemas.HabitLogCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):

    habit = db.query(models.Habit).filter(
        models.Habit.id == habit_id,
        models.Habit.use_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    log = models.HabitLog(
        **log_in.model_dump(),
        habit_id=habit.id
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

@router.get("/{habit_id}/logs", response_model=List[schemas.HabitLogOut])
def read_habit_logs(
    habit_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    habit = db.query(models.Habit).filter(
        models.Habit.id == habit_id,
        models.Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    logs = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id
    ).order_by(desc(models.HabitLog.completed_at)).offset(skip).limit(limit).all()
    return logs    





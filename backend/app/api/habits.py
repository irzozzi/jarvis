from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID
from typing import List
from datetime import datetime

from .. import schemas, models
from ..api import deps
from ..services import stats as stats_service
from ..services import prediction as prediction_service
from ..services import charts as charts_service

def validate_schedule(schedule: dict | None) -> None:
    if schedule is None:
        return
    # старый формат: {"days": [1,3,5]}
    if "days" in schedule:
        if not isinstance(schedule["days"], list) or not all(isinstance(d, int) for d in schedule["days"]):
            raise HTTPException(status_code=400, detail="Invalid schedule: 'days' must be a list of integers")
        return
    # новый формат
    if "type" not in schedule:
        raise HTTPException(status_code=400, detail="Invalid schedule: missing 'type'")
    rec_type = schedule["type"]
    if rec_type == "every_n_days":
        if "interval" not in schedule or not isinstance(schedule["interval"], int):
            raise HTTPException(status_code=400, detail="Invalid schedule: 'every_n_days' requires 'interval' integer")
    elif rec_type == "monthly":
        if "day_of_month" not in schedule or not isinstance(schedule["day_of_month"], int):
            raise HTTPException(status_code=400, detail="Invalid schedule: 'monthly' requires 'day_of_month' integer")
        if schedule["day_of_month"] < 1 or schedule["day_of_month"] > 31:
            raise HTTPException(status_code=400, detail="Invalid schedule: 'day_of_month' must be between 1 and 31")
    elif rec_type == "custom_dates":
        if "dates" not in schedule or not isinstance(schedule["dates"], list):
            raise HTTPException(status_code=400, detail="Invalid schedule: 'custom_dates' requires 'dates' list")
        # проверяем каждую дату на формат YYYY-MM-DD
        for date_str in schedule["dates"]:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid date format: '{date_str}'. Expected YYYY-MM-DD")
    else:
        raise HTTPException(status_code=400, detail=f"Invalid schedule: unknown type '{rec_type}'")

router = APIRouter(prefix="/habits", tags=["habits"])


# ---------- Статические маршруты ----------
@router.get("/stats")
def get_overall_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    stats = stats_service.get_overall_stats(db, current_user.id)
    return stats


@router.get("/chart")
def get_habits_chart(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    days: int = 30,
):
    data = charts_service.get_habit_chart_data_for_user(db, current_user.id, days)
    return data


@router.get("/", response_model=List[schemas.HabitOut])
def read_habits(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    habits = db.query(models.Habit).filter(
        models.Habit.user_id == current_user.id,
        models.Habit.deleted_at == None
    ).offset(skip).limit(limit).all()
    return habits


@router.post("/", response_model=schemas.HabitOut, status_code=status.HTTP_201_CREATED)
def create_habit(
    habit_in: schemas.HabitCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    validate_schedule(habit_in.schedule)
    habit = models.Habit(
        **habit_in.model_dump(),
        user_id=current_user.id
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


# ---------- Маршруты с параметрами ----------
@router.get("/{habit_id}/stats")
def get_habit_stats(
    habit_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    habit = db.query(models.Habit).filter(
        models.Habit.id == habit_id,
        models.Habit.user_id == current_user.id,
        models.Habit.deleted_at == None
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    stats = stats_service.get_habit_stats(db, habit)
    return stats


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
        models.Habit.user_id == current_user.id,
        models.Habit.deleted_at == None
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    logs = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id
    ).order_by(desc(models.HabitLog.completed_at)).offset(skip).limit(limit).all()
    return logs


@router.post("/{habit_id}/logs", response_model=schemas.HabitLogOut, status_code=status.HTTP_201_CREATED)
def create_habit_log(
    habit_id: UUID,
    log_in: schemas.HabitLogCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    habit = db.query(models.Habit).filter(
        models.Habit.id == habit_id,
        models.Habit.user_id == current_user.id,
        models.Habit.deleted_at == None
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    log = models.HabitLog(
        **log_in.model_dump(exclude={"habit_id"}),
        habit_id=habit_id
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/{habit_id}", response_model=schemas.HabitOut)
def read_habit(
    habit_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    habit = db.query(models.Habit).filter(
        models.Habit.id == habit_id,
        models.Habit.user_id == current_user.id,
        models.Habit.deleted_at == None
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
        models.Habit.user_id == current_user.id,
        models.Habit.deleted_at == None
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
        models.Habit.user_id == current_user.id,
        models.Habit.deleted_at == None
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    habit.deleted_at = datetime.utcnow()
    db.commit()
    return None


@router.patch("/{habit_id}/restore", response_model=schemas.HabitOut)
def restore_habit(
    habit_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Восстанавливает мягко удалённую привычку (устанавливает deleted_at = None).
    """
    habit = db.query(models.Habit).filter(
        models.Habit.id == habit_id,
        models.Habit.user_id == current_user.id,
        models.Habit.deleted_at != None
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Deleted habit not found")
    habit.deleted_at = None
    db.commit()
    db.refresh(habit)
    return habit


@router.get("/{habit_id}/predict")
def predict_relapse(
    habit_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    habit = db.query(models.Habit).filter(
        models.Habit.id == habit_id,
        models.Habit.user_id == current_user.id,
        models.Habit.deleted_at == None
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    result = prediction_service.predict_relapse_risk(db, habit, current_user.id)
    return result
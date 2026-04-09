from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from datetime import datetime

from .. import schemas, models
from ..api import deps
from ..services import goal_analyzer
from ..services import charts as charts_service
from ..schemas import ChartPoint

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("/", response_model=schemas.GoalOut, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal_in: schemas.GoalCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    category_id = goal_in.category_id
    if goal_in.custom_text and not category_id:
        analysis = goal_analyzer.analyze_custom_text(goal_in.custom_text)
        cat = db.query(models.GoalCategory).filter(
            models.GoalCategory.name.ilike(analysis["category"])
        ).first()
        if cat:
            category_id = cat.id
    goal = models.Goal(
        user_id=current_user.id,
        category_id=category_id,
        title=goal_in.title or "Новая цель",
        description=goal_in.description,
        custom_text=goal_in.custom_text,
        target_date=goal_in.target_date,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.get("/", response_model=List[schemas.GoalOut])
def read_goals(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    goals = db.query(models.Goal).filter(
        models.Goal.user_id == current_user.id,
        models.Goal.deleted_at == None
    ).order_by(models.Goal.created_at.desc()).offset(skip).limit(limit).all()
    return goals


@router.get("/{goal_id}", response_model=schemas.GoalOut)
def read_goal(
    goal_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id,
        models.Goal.deleted_at == None
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.put("/{goal_id}", response_model=schemas.GoalOut)
def update_goal(
    goal_id: UUID,
    goal_in: schemas.GoalUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id,
        models.Goal.deleted_at == None
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    old_progress = goal.progress
    for field, value in goal_in.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    if goal.progress != old_progress:
        log_entry = models.GoalProgressLog(
            goal_id=goal.id,
            progress=goal.progress
        )
        db.add(log_entry)
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id,
        models.Goal.deleted_at == None
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    goal.deleted_at = datetime.utcnow()
    db.commit()
    return None


@router.patch("/{goal_id}/restore", response_model=schemas.GoalOut)
def restore_goal(
    goal_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id,
        models.Goal.deleted_at != None
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Deleted goal not found")
    goal.deleted_at = None
    db.commit()
    db.refresh(goal)
    return goal


@router.post("/{goal_id}/habits/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_habit_to_goal(
    goal_id: UUID,
    habit_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id,
        models.Goal.deleted_at == None
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    habit = db.query(models.Habit).filter(
        models.Habit.id == habit_id,
        models.Habit.user_id == current_user.id,
        models.Habit.deleted_at == None
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    stmt = models.goal_habits.select().where(
        models.goal_habits.c.goal_id == goal_id,
        models.goal_habits.c.habit_id == habit_id
    )
    exists = db.execute(stmt).first()
    if exists:
        raise HTTPException(status_code=400, detail="Habit already linked to this goal")
    ins = models.goal_habits.insert().values(goal_id=goal_id, habit_id=habit_id)
    db.execute(ins)
    db.commit()
    return None


@router.delete("/{goal_id}/habits/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_habit_from_goal(
    goal_id: UUID,
    habit_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id,
        models.Goal.deleted_at == None
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    stmt = models.goal_habits.delete().where(
        models.goal_habits.c.goal_id == goal_id,
        models.goal_habits.c.habit_id == habit_id
    )
    result = db.execute(stmt)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Habit not linked to this goal")
    return None


@router.get("/chart/{goal_id}", response_model=List[ChartPoint])
def get_goal_chart(
    goal_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    days: int = 90,
):
    points = charts_service.get_goal_progress_chart(db, current_user.id, str(goal_id), days)
    return [{"date": p[0], "value": p[1]} for p in points]


@router.get("/{goal_id}/history")
def get_goal_history(
    goal_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id,
        models.Goal.deleted_at == None
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    history = db.query(models.GoalProgressLog).filter(
        models.GoalProgressLog.goal_id == goal_id
    ).order_by(models.GoalProgressLog.created_at).all()
    return [{"date": h.created_at.isoformat(), "progress": h.progress} for h in history]



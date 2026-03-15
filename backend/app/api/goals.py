from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from .. import schemas, models
from ..api import deps
from ..services import goal_analyzer

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("/", response_model=schemas.GoalOut, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal_in: schemas.GoalCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Создаёт новую цель. Если передан custom_text, анализирует его для определения категории.
    """
    category_id = goal_in.category_id

    if goal_in.custom_text and not category_id:
        analysis = goal_analyzer.analyze_custom_text(goal_in.custom_text)
        # Используем ilike для регистронезависимого поиска
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
    """
    Список целей пользователя.
    """
    goals = db.query(models.Goal).filter(
        models.Goal.user_id == current_user.id
    ).order_by(models.Goal.created_at.desc()).offset(skip).limit(limit).all()
    return goals


@router.get("/{goal_id}", response_model=schemas.GoalOut)
def read_goal(
    goal_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Детали цели.
    """
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
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
    """
    Обновление цели.
    """
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    for field, value in goal_in.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)

    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Удаление цели.
    """
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
    return None


@router.post("/{goal_id}/habits/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_habit_to_goal(
    goal_id: UUID,
    habit_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Привязывает привычку к цели.
    """
    # Проверяем, что цель принадлежит пользователю
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    # Проверяем, что привычка принадлежит пользователю
    habit = db.query(models.Habit).filter(
        models.Habit.id == habit_id,
        models.Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    # Проверяем, не привязана ли уже
    stmt = models.goal_habits.select().where(
        models.goal_habits.c.goal_id == goal_id,
        models.goal_habits.c.habit_id == habit_id
    )
    exists = db.execute(stmt).first()
    if exists:
        raise HTTPException(status_code=400, detail="Habit already linked to this goal")

    # Добавляем связь
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
    """
    Убирает привычку из цели.
    """
    # Проверяем, что цель принадлежит пользователю
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    # Удаляем связь
    stmt = models.goal_habits.delete().where(
        models.goal_habits.c.goal_id == goal_id,
        models.goal_habits.c.habit_id == habit_id
    )
    result = db.execute(stmt)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Habit not linked to this goal")
    return None
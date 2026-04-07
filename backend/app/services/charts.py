from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import List, Tuple, Optional
from .. import models

def _group_points(points: List[Tuple[date, float]], group_by: str) -> List[Tuple[date, float]]:
    """Группирует точки (дата, значение) по неделям или месяцам."""
    if group_by == "day" or not points:
        return points
    result = []
    if group_by == "week":
        weeks = {}
        for d, val in points:
            start_of_week = d - timedelta(days=d.weekday())  # понедельник
            weeks.setdefault(start_of_week, []).append(val)
        for start_of_week, vals in sorted(weeks.items()):
            avg_val = sum(vals) / len(vals)
            result.append((start_of_week, avg_val))
    elif group_by == "month":
        months = {}
        for d, val in points:
            month_key = d.replace(day=1)
            months.setdefault(month_key, []).append(val)
        for month_start, vals in sorted(months.items()):
            avg_val = sum(vals) / len(vals)
            result.append((month_start, avg_val))
    return result

def get_habit_completion_chart(
    db: Session,
    user_id: str,
    habit_id: Optional[str] = None,
    days: int = 30,
    group_by: str = "day"
) -> List[Tuple[date, float]]:
    """
    Возвращает список (дата, процент выполнения) для всех привычек
    или для одной привычки за последние `days` дней.
    """
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days - 1)

    query = db.query(models.HabitLog).join(models.Habit).filter(
        models.Habit.user_id == user_id,
        models.HabitLog.completed_at >= start_date,
        models.HabitLog.completed_at <= datetime.utcnow(),
        models.Habit.deleted_at == None
    )
    if habit_id:
        query = query.filter(models.Habit.id == habit_id)

    logs = query.all()

    logs_by_date = {}
    for log in logs:
        log_date = log.completed_at.date()
        logs_by_date.setdefault(log_date, []).append(log)

    if habit_id:
        active_habits_count = 1
    else:
        active_habits_count = db.query(models.Habit).filter(
            models.Habit.user_id == user_id,
            models.Habit.is_active == True,
            models.Habit.deleted_at == None
        ).count()
        if active_habits_count == 0:
            active_habits_count = 1

    points = []
    current = start_date
    while current <= end_date:
        logs_today = logs_by_date.get(current, [])
        if habit_id:
            completion_rate = 100.0 if logs_today else 0.0
        else:
            completed_habits = len(logs_today)
            completion_rate = (completed_habits / active_habits_count) * 100.0
        points.append((current, completion_rate))
        current += timedelta(days=1)

    # Применяем группировку
    return _group_points(points, group_by)

def get_habit_chart_data_for_user(
    db: Session,
    user_id: str,
    days: int = 30,
    group_by: str = "day"
) -> dict:
    """
    Возвращает данные для графиков: список привычек с их ID и названиями,
    а также общую кривую выполнения.
    """
    habits = db.query(models.Habit).filter(
        models.Habit.user_id == user_id,
        models.Habit.is_active == True,
        models.Habit.deleted_at == None
    ).all()

    overall = get_habit_completion_chart(db, user_id, days=days, group_by=group_by)
    per_habit = []
    for habit in habits:
        points = get_habit_completion_chart(db, user_id, str(habit.id), days, group_by)
        per_habit.append({
            "habit_id": str(habit.id),
            "habit_name": habit.name,
            "data": [{"date": p[0], "value": p[1]} for p in points]
        })

    return {
        "overall": [{"date": p[0], "value": p[1]} for p in overall],
        "habits": per_habit
    }

def get_goal_progress_chart(
    db: Session,
    user_id: str,
    goal_id: Optional[str] = None,
    days: int = 90
) -> List[Tuple[date, float]]:
    """
    Возвращает прогресс по целям за последние days дней.
    Для простоты вернём серию точек с одинаковым значением текущего прогресса.
    """
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days - 1)

    if goal_id:
        goal = db.query(models.Goal).filter(
            models.Goal.id == goal_id,
            models.Goal.user_id == user_id,
            models.Goal.deleted_at == None
        ).first()
        if not goal:
            return []
        current_progress = goal.progress
    else:
        return []

    result = []
    current = start_date
    while current <= end_date:
        result.append((current, current_progress))
        current += timedelta(days=1)
    return result
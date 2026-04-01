from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from .. import models

def calculate_streak(logs: List[models.HabitLog]) -> int:
    if not logs:
        return 0
    sorted_logs = sorted(logs, key=lambda x: x.completed_at, reverse=True)
    today = datetime.utcnow().date()
    last_log_date = sorted_logs[0].completed_at.date()
    if last_log_date != today:
        return 0
    streak = 1
    current_date = today
    for log in sorted_logs[1:]:
        log_date = log.completed_at.date()
        if (current_date - log_date).days == 1:
            streak += 1
            current_date = log_date
        else:
            break
    return streak

def is_expected_date(date: date, schedule: dict, habit_created_at: datetime) -> bool:
    """
    Определяет, ожидается ли выполнение привычки в указанную дату.
    """
    if not schedule:
        return True  # ежедневно

    # Обратная совместимость: старый формат {"days": [1,3,5], "time": "07:00"}
    if "days" in schedule:
        return date.isoweekday() in schedule["days"]

    rec_type = schedule.get("type")
    if rec_type == "weekly":
        days_list = schedule.get("days", [])
        return date.isoweekday() in days_list
    elif rec_type == "every_n_days":
        interval = schedule.get("interval", 1)
        start_date = habit_created_at.date()
        days_since_start = (date - start_date).days
        return days_since_start >= 0 and days_since_start % interval == 0
    elif rec_type == "monthly":
        day_of_month = schedule.get("day_of_month")
        if day_of_month is not None:
            return date.day == day_of_month
        return False
    elif rec_type == "custom_dates":
        custom_dates = schedule.get("dates", [])
        return date.isoformat() in custom_dates
    else:
        return False

def calculate_completion_rate(
    logs: List[models.HabitLog],
    days: int,
    schedule: Optional[dict] = None,
    habit_created_at: Optional[datetime] = None,
) -> float:
    if not logs:
        return 0.0

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days - 1)

    log_dates = {log.completed_at.date() for log in logs if log.completed_at.date() >= start_date}

    expected_dates = []
    current = start_date
    while current <= end_date:
        if schedule and habit_created_at:
            if is_expected_date(current, schedule, habit_created_at):
                expected_dates.append(current)
        else:
            expected_dates.append(current)
        current += timedelta(days=1)

    completed_days = sum(1 for date in expected_dates if date in log_dates)
    total_expected = len(expected_dates)

    if total_expected == 0:
        return 0.0
    return round((completed_days / total_expected) * 100, 2)

def get_habit_stats(db: Session, habit: models.Habit) -> Dict[str, Any]:
    logs = db.query(models.HabitLog).filter(models.HabitLog.habit_id == habit.id).all()
    streak = calculate_streak(logs)
    rate_7d = calculate_completion_rate(logs, 7, habit.schedule, habit.created_at)
    rate_30d = calculate_completion_rate(logs, 30, habit.schedule, habit.created_at)

    avg_value = None
    if habit.type == 'numeric' and logs:
        values = [log.value for log in logs]
        avg_value = sum(values) / len(values)

    return {
        "habit_id": habit.id,
        "streak": streak,
        "completion_rate_7d": rate_7d,
        "completion_rate_30d": rate_30d,
        "average_value": avg_value,
        "total_logs": len(logs)
    }

def get_overall_stats(db: Session, user_id: str) -> Dict[str, Any]:
    habits = db.query(models.Habit).filter(
        models.Habit.user_id == user_id,
        models.Habit.deleted_at == None
    ).all()
    total_habits = len(habits)
    active_habits = sum(1 for h in habits if h.is_active)

    total_logs = 0
    streaks = []
    for habit in habits:
        logs = db.query(models.HabitLog).filter(models.HabitLog.habit_id == habit.id).all()
        total_logs += len(logs)
        streaks.append(calculate_streak(logs))

    avg_streak = round(sum(streaks) / len(streaks), 2) if streaks else 0
    max_streak = max(streaks) if streaks else 0

    return {
        "total_habits": total_habits,
        "active_habits": active_habits,
        "total_logs": total_logs,
        "average_streak": avg_streak,
        "max_streak": max_streak
    }
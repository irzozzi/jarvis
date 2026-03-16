from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .. import models
from typing import List, Dict, Any, Optional

def calculate_streak(logs: List[models.HabitLog]) -> int:
    """
    Рассчитывает текущую серию выполнения привычки на основе логов.
    Серия считается как количество последовательных дней, в которые есть логи.
    Если сегодня нет лога, серия сбрасывается.
    """
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

def calculate_completion_rate(
    logs: List[models.HabitLog],
    days: int,
    schedule: Optional[dict] = None
) -> float:
    """
    Рассчитывает процент выполнения за последние N дней с учетом расписания.
    schedule может содержать ключ 'days' со списком дней недели (1-пн, 7-вс).
    Если schedule не указан или 'days' отсутствует, привычка считается ежедневной.
    """
    if not logs:
        return 0.0

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days - 1)

    log_dates = {log.completed_at.date() for log in logs if log.completed_at.date() >= start_date}

    expected_dates = []
    current = start_date
    while current <= end_date:
        if schedule and schedule.get('days'):
            if current.isoweekday() in schedule['days']:
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
    """
    Возвращает статистику для конкретной привычки.
    """
    logs = db.query(models.HabitLog).filter(models.HabitLog.habit_id == habit.id).all()

    streak = calculate_streak(logs)
    rate_7d = calculate_completion_rate(logs, 7, habit.schedule)
    rate_30d = calculate_completion_rate(logs, 30, habit.schedule)

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

def get_overall_stats(db: Session, user_id: str) -> Dict [str, Any]:
    """
    Общая статистика по всем привычкам пользователя.
    """
    habits = db.query(models.Habit).filter(models.Habit.user_id == user_id).all()
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

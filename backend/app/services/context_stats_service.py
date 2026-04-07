from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict
from ..models.habit_log import HabitLog
from ..models.context import Context
from ..models.habit import Habit


def get_time_of_day(hour: int) -> str:
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 22:
        return "evening"
    else:
        return "night"


def get_context_stats(
    db: Session,
    user_id: str,
    start_date: datetime,
    end_date: datetime
) -> Dict:
    # Запрос: логи привычек пользователя с контекстом за период
    rows = (
        db.query(HabitLog, Context)
        .join(Habit, HabitLog.habit_id == Habit.id)
        .outerjoin(Context, HabitLog.context_id == Context.id)
        .filter(
            Habit.user_id == user_id,
            HabitLog.completed_at >= start_date,
            HabitLog.completed_at <= end_date,
            Habit.deleted_at.is_(None)
        )
        .all()
    )

    stats = {
        "by_location_type": {},
        "by_activity": {},
        "by_time_of_day": {},
        "by_weather": {}
    }

    for log, ctx in rows:
        if not ctx:
            continue

        # Считаем лог выполненным, если value > 0 (для boolean/numeric/timer)
        completed = 1 if log.value > 0 else 0

        # 1. Тип локации
        loc = ctx.location_type or "unknown"
        _update_dict(stats["by_location_type"], loc, completed)

        # 2. Активность
        act = ctx.activity or "unknown"
        _update_dict(stats["by_activity"], act, completed)

        # 3. Время суток
        tod = get_time_of_day(ctx.timestamp.hour)
        _update_dict(stats["by_time_of_day"], tod, completed)

        # 4. Погода
        if ctx.weather and isinstance(ctx.weather, dict):
            weather_main = ctx.weather.get("main", "unknown")
            _update_dict(stats["by_weather"], weather_main, completed)

    # Преобразуем в проценты
    for category in stats.values():
        for key, data in category.items():
            total = data["total"]
            if total > 0:
                data["rate"] = round(data["completed"] / total * 100, 1)
            else:
                data["rate"] = 0
    return stats


def _update_dict(container: Dict, key: str, completed: int):
    if key not in container:
        container[key] = {"completed": 0, "total": 0}
    container[key]["completed"] += completed
    container[key]["total"] += 1
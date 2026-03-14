from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .. import models
import logging

logger = logging.getLogger(__name__)

def analyze_time_patterns(db: Session, user_id: str, habit_id: str = None) -> List[Dict[str, Any]]:
    """
    Анализирует временные паттерны: в какие часы пользователь чаще выполняет привычки,
    в какие дни недели пропускает и т.д.
    Возвращает список инсайтов (словарей), готовых к сохранению.
    """
    insights = []
    
    # Базовый запрос логов пользователя
    query = db.query(models.HabitLog).join(models.Habit).filter(models.Habit.user_id == user_id)
    if habit_id:
        query = query.filter(models.HabitLog.habit_id == habit_id)
    
    logs = query.all()
    if len(logs) < 3:  # недостаточно данных
        return insights
    
    # Анализ времени суток
    hour_counts = {}
    for log in logs:
        hour = log.completed_at.hour
        hour_counts[hour] = hour_counts.get(hour, 0) + 1
    
    if hour_counts:
        peak_hour = max(hour_counts, key=hour_counts.get)
        insights.append({
            "habit_id": habit_id,
            "type": "time_pattern",
            "content": f"Ты чаще всего выполняешь привычку в {peak_hour}:00. Отличное время!",
            "data": {"peak_hour": peak_hour, "distribution": hour_counts}
        })
    
    # Анализ дней недели
    day_counts = {}
    for log in logs:
        day = log.completed_at.isoweekday()  # 1-пн, 7-вс
        day_counts[day] = day_counts.get(day, 0) + 1
    
    if day_counts:
        best_day = max(day_counts, key=day_counts.get)
        days_map = {1: "пн", 2: "вт", 3: "ср", 4: "чт", 5: "пт", 6: "сб", 7: "вс"}
        insights.append({
            "habit_id": habit_id,
            "type": "time_pattern",
            "content": f"Твой самый продуктивный день — {days_map[best_day]}!",
            "data": {"best_day": best_day, "distribution": day_counts}
        })
    
    return insights


def analyze_context_patterns(db: Session, user_id: str) -> List[Dict[str, Any]]:
    """
    Анализирует контекстные паттерны (пока заглушка, так как контекст ещё не собираем).
    Позже здесь будет анализ геолокации, активности и т.д.
    """
    # Пока контекст не собирается, возвращаем пустой список.
    # В будущем здесь будет реальный анализ.
    return []


def find_keystone_habits(db: Session, user_id: str) -> List[Dict[str, Any]]:
    """
    Ищет ключевые привычки — те, выполнение которых повышает вероятность выполнения других.
    Использует простую корреляцию (пока rule-based, позже можно улучшить).
    """
    # Получаем все привычки пользователя
    habits = db.query(models.Habit).filter(models.Habit.user_id == user_id).all()
    if len(habits) < 2:
        return []
    
    # Для простоты возьмём привычку с наибольшим количеством логов как потенциально ключевую
    # В реальности нужно считать корреляции выполнения в один день и т.д.
    habit_log_counts = []
    for h in habits:
        count = db.query(models.HabitLog).filter(models.HabitLog.habit_id == h.id).count()
        habit_log_counts.append((h, count))
    
    if not habit_log_counts:
        return []
    
    # Отсортируем по убыванию логов и возьмём топ-1
    habit_log_counts.sort(key=lambda x: x[1], reverse=True)
    top_habit, top_count = habit_log_counts[0]
    
    insights = []
    if top_count > 0:
        insights.append({
            "habit_id": top_habit.id,
            "type": "keystone_habit",
            "content": f"Привычка «{top_habit.name}» — твоя ключевая. Когда ты её делаешь, другие идут легче!",
            "data": {"habit_name": top_habit.name, "log_count": top_count}
        })
    
    return insights


def generate_all_insights(db: Session, user_id: str) -> List[models.Insight]:
    """
    Генерирует все новые инсайты для пользователя и сохраняет их в БД.
    Возвращает список созданных объектов Insight.
    """
    new_insights = []
    
    # Временные паттерны для всех привычек вместе и для каждой отдельно
    patterns = analyze_time_patterns(db, user_id)
    new_insights.extend(patterns)
    
    # Для каждой привычки отдельно (если хотим)
    habits = db.query(models.Habit).filter(models.Habit.user_id == user_id).all()
    for habit in habits:
        habit_patterns = analyze_time_patterns(db, user_id, str(habit.id))
        new_insights.extend(habit_patterns)
    
    # Контекстные паттерны (пока пусто)
    context = analyze_context_patterns(db, user_id)
    new_insights.extend(context)
    
    # Ключевые привычки
    keystone = find_keystone_habits(db, user_id)
    new_insights.extend(keystone)
    
    # Сохраняем инсайты в БД
    saved = []
    for insight_data in new_insights:
        # Проверим, нет ли уже похожего непрочитанного инсайта за последние 7 дней
        existing = db.query(models.Insight).filter(
            models.Insight.user_id == user_id,
            models.Insight.type == insight_data["type"],
            models.Insight.habit_id == insight_data.get("habit_id"),
            models.Insight.is_read == False,
            models.Insight.created_at >= datetime.utcnow() - timedelta(days=7)
        ).first()
        if existing:
            continue  # пропускаем дубликаты
        
        insight = models.Insight(
            user_id=user_id,
            habit_id=insight_data.get("habit_id"),
            type=insight_data["type"],
            content=insight_data["content"],
            data=insight_data.get("data")
        )
        db.add(insight)
        saved.append(insight)
    
    if saved:
        db.commit()
        for insight in saved:
            db.refresh(insight)
    
    return saved
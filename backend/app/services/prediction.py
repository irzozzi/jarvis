from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Dict, Any
from .. import models

def predict_relapse_risk(db: Session, habit: models.Habit, user_id: str) -> Dict[str, Any]:
    """
    Оценивает риск срыва для привычки на основе истории и контекста.
    Возвращает словарь с уровнем риска ('low', 'medium', 'high') и сообщением.
    """
    logs = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit.id
    ).order_by(models.HabitLog.completed_at.desc()).all()

    # Если нет логов – низкий риск (нечего срывать)
    if not logs:
        return {
            "risk": "low",
            "message": "У тебя пока нет логов по этой привычке. Начни сегодня!",
            "details": {}
        }

    today = datetime.utcnow().date()
    last_log_date = logs[0].completed_at.date()
    days_since_last = (today - last_log_date).days

    risk_score = 0
    reasons = []

    # 1. Последний лог
    if last_log_date == today:
        risk_score += 10
        reasons.append("Ты уже выполнил привычку сегодня.")
    else:
        if days_since_last == 1:
            risk_score += 30
            reasons.append("Пропуск вчера.")
        elif days_since_last == 2:
            risk_score += 50
            reasons.append("Пропуск два дня подряд.")
        elif days_since_last >= 3:
            risk_score += 80
            reasons.append(f"Пропуск {days_since_last} дней.")

    # 2. Анализ настроения в последнем логе
    if logs[0].mood and logs[0].mood <= 2:
        risk_score += 15
        reasons.append("В прошлый раз настроение было низким.")

    # 3. Контекст за последние 24 часа
    recent_context = db.query(models.Context).filter(
        models.Context.user_id == user_id,
        models.Context.timestamp >= datetime.utcnow() - timedelta(days=1)
    ).order_by(models.Context.timestamp.desc()).first()

    if recent_context:
        hour = recent_context.timestamp.hour
        if recent_context.activity == "stationary" and (hour >= 22 or hour <= 5):
            risk_score += 20
            reasons.append("Позднее время и низкая активность.")
        if recent_context.location_type in ["cafe", "bar"]:
            risk_score += 15
            reasons.append("Ты в месте, где может быть сложнее удержаться.")

    # Определение уровня риска
    if risk_score < 30:
        risk_level = "low"
        message = "Всё идёт хорошо, продолжай в том же духе."
    elif risk_score < 60:
        risk_level = "medium"
        message = "Есть небольшой риск срыва. Обрати внимание на свою мотивацию."
    else:
        risk_level = "high"
        message = "Высокий риск срыва! Самое время вспомнить, зачем ты это делаешь."

    return {
        "risk": risk_level,
        "score": risk_score,
        "message": message,
        "details": {
            "days_since_last": days_since_last,
            "reasons": reasons,
            "last_log_date": last_log_date.isoformat() if logs else None
        }
    }
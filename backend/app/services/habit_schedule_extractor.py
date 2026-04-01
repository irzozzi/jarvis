import json
import re
from .llm_service import ask_yandex_gpt

async def extract_habit_schedule(user_message: str):
    """
    Извлекает правила повторения привычки из сообщения пользователя.
    Возвращает словарь schedule или None.
    """
    prompt = f"""Извлеки из следующего сообщения пользователя правила повторения для привычки. Верни JSON.

Возможные типы:
- weekly (по дням недели): {{"type": "weekly", "days": [1,2,3]}} где 1-пн, 7-вс
- every_n_days (каждые N дней): {{"type": "every_n_days", "interval": N}}
- monthly (ежемесячно): {{"type": "monthly", "day_of_month": число}}
- custom_dates (конкретные даты): {{"type": "custom_dates", "dates": ["YYYY-MM-DD", ...]}}
- если расписание не указано или не удаётся распознать, верни null

Сообщение: {user_message}
"""
    response = await ask_yandex_gpt(prompt)
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if not json_match:
        return None
    try:
        data = json.loads(json_match.group())
        if data is None or "type" not in data:
            return None
        return data
    except json.JSONDecodeError:
        return None
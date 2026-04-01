import json
import re
from datetime import datetime, timedelta
from .llm_service import ask_yandex_gpt

async def extract_event_data(user_message: str) -> dict:
    """
    Возвращает словарь с полями:
    - status: "success", "missing_date", "missing_time", "missing_both", "cannot_parse"
    - data: если status "success", то словарь с title, start_time, end_time
    - message: если есть уточнение
    """
    prompt = f"""Проанализируй сообщение пользователя. Если в нём есть название события, дата и время, верни JSON:
{{"status": "success", "title": "название", "start": "YYYY-MM-DD HH:MM:SS", "duration_hours": 1}}

Если есть название, но нет даты, верни:
{{"status": "missing_date", "title": "название"}}

Если есть название и дата, но нет времени, верни:
{{"status": "missing_time", "title": "название", "date": "YYYY-MM-DD"}}

Если нет ни даты, ни времени, верни:
{{"status": "missing_both"}}

Если вообще не удалось извлечь смысл, верни:
{{"status": "cannot_parse"}}

Сообщение: {user_message}
"""

    response = await ask_yandex_gpt(prompt)
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if not json_match:
        return {"status": "cannot_parse"}
    try:
        data = json.loads(json_match.group())
    except json.JSONDecodeError:
        return {"status": "cannot_parse"}

    status = data.get("status")
    if status == "success":
        try:
            start_time = datetime.strptime(data["start"], "%Y-%m-%d %H:%M:%S")
            duration = data.get("duration_hours", 1)
            end_time = start_time + timedelta(hours=duration)
            return {
                "status": "success",
                "data": {
                    "title": data["title"],
                    "start_time": start_time,
                    "end_time": end_time
                }
            }
        except Exception:
            return {"status": "cannot_parse"}
    elif status == "missing_date":
        return {
            "status": "missing_date",
            "title": data.get("title", "событие")
        }
    elif status == "missing_time":
        return {
            "status": "missing_time",
            "title": data.get("title", "событие"),
            "date": data.get("date")
        }
    elif status == "missing_both":
        return {"status": "missing_both"}
    else:
        return {"status": "cannot_parse"}
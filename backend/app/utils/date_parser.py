import re
from datetime import datetime, timedelta

def parse_datetime(text: str) -> tuple[datetime, datetime] | None:
    """
    Пытается извлечь дату и время из текста. Возвращает (start_time, end_time).
    Поддерживает "сегодня в HH:MM" и "завтра в HH:MM"
    """

    text_lower = text.lower()
    now = datetime.utcnow()

    match = re.search(r'завтра в (\d{1,2}):(\d{2})', text_lower)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        start = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=1)
        if start <= now:
            start += timedelta(days=1)
        end = start + timedelta(hours=1)
        return start, end
    
    match = re.search(r'сегодня в (\d{1,2}):(\d{2})', text_lower)
    if match: 
        hour = int(match.group(1))
        minute = int(match.group(2))
        start = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if start <= now:
            start += timedelta(days=1)
        end = start + timedelta(hours=1)
        return start, end
    
    return None
                                                                            

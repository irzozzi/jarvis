import re
from typing import Tuple, Optional

# Словарь интентов с ключевыми словами
INTENTS = {
    "greeting": ["привет", "здравствуй", "добрый день", "доброе утро", "добрый вечер", "хай", "здорово"],
    "farewell": ["пока", "до свидания", "до встречи", "всего доброго", "увидимся"],
    "stats": ["статистика", "успехи", "прогресс", "как дела", "что нового", "достижения", "сколько", "серия"],
    "insight": ["инсайт", "совет", "подсказка", "анализ", "закономерность", "почему", "заметил"],
    "motivation": ["мотивация", "поддержка", "не хочу", "лень", "устал", "сложно", "трудно", "помоги"],
    "help": ["помощь", "помоги", "help", "что ты умеешь", "функции"],
    "goal": ["цель", "цели", "план", "достичь", "мечта"],
    "habit": ["привычка", "привычки", "трекер", "выполнил"],
    "context": ["где я", "погода", "время", "сколько времени"],
}

def classify_intent(text: str) -> Tuple[str, Optional[str]]:
    """
    Определяет интент сообщения и возвращает (intent_name, matched_keyword)
    """
    text_lower = text.lower().strip()
    # Убираем знаки препинания для лучшего поиска
    text_clean = re.sub(r'[^\w\s]', '', text_lower)
    words = set(text_clean.split())
    
    for intent, keywords in INTENTS.items():
        for keyword in keywords:
            if keyword in text_lower or keyword in words:
                return intent, keyword
    return "unknown", None
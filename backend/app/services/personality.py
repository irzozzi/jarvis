from typing import List, Dict, Any
from ..schemas.personality import QuestionAnswer

# Простая rule-based модель: каждый вопрос относится к одному из типов.
# Вопросы можно расширить позже. Сейчас для примера 5 вопросов.
QUESTIONS = [
    {
        "id": 1,
        "text": "Когда ты ставишь цель, что для тебя важнее?",
        "options": {
            1: "достигатор",   # ответ 1 = достигатор
            2: "исследователь",
            3: "чувствительный",
            4: "прагматик"
        }
    },
    {
        "id": 2,
        "text": "Как ты реагируешь на неудачи?",
        "options": {
            1: "исследователь",
            2: "чувствительный",
            3: "достигатор",
            4: "прагматик"
        }
    },
    {
        "id": 3,
        "text": "Что тебя мотивирует сильнее?",
        "options": {
            1: "достигатор",
            2: "исследователь",
            3: "чувствительный",
            4: "прагматик"
        }
    },
    {
        "id": 4,
        "text": "Как часто ты любишь получать обратную связь?",
        "options": {
            1: "достигатор",
            2: "чувствительный",
            3: "исследователь",
            4: "прагматик"
        }
    },
    {
        "id": 5,
        "text": "Что для тебя развитие?",
        "options": {
            1: "достигатор",
            2: "исследователь",
            3: "чувствительный",
            4: "прагматик"
        }
    }
]

def calculate_personality_type(answers: List[QuestionAnswer]) -> str:
    """
    Подсчитывает баллы для каждого типа и возвращает тип с максимумом.
    """
    scores = {
        "достигатор": 0,
        "исследователь": 0,
        "чувствительный": 0,
        "прагматик": 0
    }

    for ans in answers:
        # находим вопрос по id
        question = next((q for q in QUESTIONS if q["id"] == ans.question_id), None)
        if question and ans.answer in question["options"]:
            ptype = question["options"][ans.answer]
            scores[ptype] += 1

    # Определяем тип с максимальным баллом
    max_type = max(scores, key=scores.get)
    return max_type
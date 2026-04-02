from .personality_questions import QUESTIONS
from typing import List, Dict, Any

def calculate_ocean_scores(answers: List[Dict[str, int]]) -> Dict[str, float]:
    scores = {
        'openness': 0,
        'conscientiousness': 0,
        'extraversion': 0,
        'agreeableness': 0,
        'neuroticism': 0
    }
    counts = {
        'openness': 0,
        'conscientiousness': 0,
        'extraversion': 0,
        'agreeableness': 0,
        'neuroticism': 0
    }

    for ans in answers:
        q_id = ans['question_id']
        value = ans['answer']  # исправлено
        question = next((q for q in QUESTIONS if q['id'] == q_id), None)
        if not question:
            continue
        factor = question['factor']
        direction = question.get('direction', 1)
        if direction == -1:
            value = 6 - value
        scores[factor] += value
        counts[factor] += 1

    for factor in scores:
        if counts[factor] > 0:
            avg = scores[factor] / counts[factor]
            scores[factor] = (avg - 1) / 4 * 100
        else:
            scores[factor] = 50.0

    return scores
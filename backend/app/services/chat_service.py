import os
import re
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from .. import models
from ..core.database import SessionLocal
from .llm_service import ask_yandex_gpt
from . import stats as stats_service
from . import intent_classifier
from ..utils.date_parser import parse_datetime
from .event_service import create_event_from_request

load_dotenv()
MAX_HISTORY = int(os.getenv("MAX_HISTORY", 20))

async def process_message(user_id: UUID, message: str) -> str:
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        personality = db.query(models.Personality).filter(
            models.Personality.user_id == user_id
        ).first()

        conversation = db.query(models.Conversation).filter(
            models.Conversation.user_id == user_id
        ).order_by(models.Conversation.updated_at.desc()).first()
        if not conversation:
            conversation = models.Conversation(user_id=user_id)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        messages_history = db.query(models.Message).filter(
            models.Message.conversation_id == conversation.id
        ).order_by(models.Message.created_at.desc()).limit(MAX_HISTORY).all()
        messages_history.reverse()

        history_lines = []
        for msg in messages_history:
            if msg.role == models.MessageRole.USER:
                history_lines.append(f"Пользователь: {msg.content}")
            else:
                history_lines.append(f"Джарвис: {msg.content}")

        history_lines.append(f"Пользователь: {message}")
        context = "\n".join(history_lines)

        user_name = user.email.split('@')[0]
        user_psychotype = personality.type if personality else "не определён"

        habits = db.query(models.Habit).filter(
            models.Habit.user_id == user_id,
            models.Habit.is_active == True
        ).limit(5).all()
        habit_lines = []
        for habit in habits:
            logs = db.query(models.HabitLog).filter(
                models.HabitLog.habit_id == habit.id
            ).all()
            streak = stats_service.calculate_streak(logs)
            rate_7d = stats_service.calculate_completion_rate(logs, 7, habit.schedule)
            habit_lines.append(
                f"- {habit.name} (цель: {habit.target} {habit.unit or ''}, "
                f"серия: {streak} дней, выполнение за 7 дней: {rate_7d}%)"
            )
        habits_text = "\n".join(habit_lines) if habit_lines else "Нет активных привычек."

        insights = db.query(models.Insight).filter(
            models.Insight.user_id == user_id,
            models.Insight.is_read == False
        ).order_by(models.Insight.created_at.desc()).limit(2).all()
        insights_text = "\n".join([f"- {ins.content}" for ins in insights]) if insights else "Нет новых инсайтов."

        goals = db.query(models.Goal).filter(
            models.Goal.user_id == user_id,
            models.Goal.status == "active"
        ).limit(3).all()
        goals_text = "\n".join([f"- {g.title} (прогресс: {g.progress}%)" for g in goals]) if goals else "Нет активных целей."

        prompt = f"""Ты — Джарвис, персональный AI-ассистент по формированию привычек.
Пользователь: {user_name}
Психотип: {user_psychotype}

Данные пользователя:
Привычки:
{habits_text}

Инсайты:
{insights_text}

Цели:
{goals_text}

История диалога:
{context}

Ответь кратко, по делу, поддерживающе. Учитывай психотип пользователя."""

        response = await ask_yandex_gpt(prompt)

        # Обработка планирования
        intent, _ = intent_classifier.classify_intent(message)
        if intent == "planning":
            parsed = parse_datetime(message)
            if parsed:
                start_time, end_time = parsed
                title = "Запланированное событие"
                match = re.search(r'(?i)(запланируй|создай событие|напомни|добавь в календарь)\s+(.+?)\s+(?:на|в|сегодня|завтра)', message)
                if match:
                    title = match.group(2).strip()
                event = create_event_from_request(
                    db=db,
                    user_id=user_id,
                    title=title,
                    start_time=start_time,
                    end_time=end_time,
                    description=message
                )
                response += f"\n\n Я создал событие: «{event.title}» на {event.start_time.strftime('%d.%m.%Y %H:%M')}."

        # Сохраняем сообщения
        user_msg = models.Message(
            conversation_id=conversation.id,
            role=models.MessageRole.USER,
            content=message
        )
        db.add(user_msg)

        assistant_msg = models.Message(
            conversation_id=conversation.id,
            role=models.MessageRole.ASSISTANT,
            content=response
        )
        db.add(assistant_msg)

        conversation.updated_at = datetime.utcnow()
        db.commit()

        return response

    finally:
        db.close()
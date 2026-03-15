from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from .. import models, schemas
import logging

logger = logging.getLogger(__name__)

async def process_message(user_id: UUID, message: str, db: Session) -> str:
    """
    Обрабатывает входящее сообщение от пользователя.
    Определяет интент, генерирует ответ, сохраняет диалог.
    """
    # Здесь будет определение интента и выбор ответа
    # Пока простая заглушка
    response = generate_response(message)
    # Сохраняем сообщение пользователя и ответ ассистента
    # Для простоты будем использовать одну беседу на пользователя
    conversation = db.query(models.Conversation).filter(
        models.Conversation.user_id == user_id
    ).order_by(models.Conversation.updated_at.desc()).first()
    if not conversation:
        conversation = models.Conversation(user_id=user_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    # Сохраняем сообщение пользователя
    user_msg = models.Message(
        conversation_id=conversation.id,
        role=models.MessageRole.USER,
        content=message
    )
    db.add(user_msg)
    # Сохраняем ответ ассистента
    assistant_msg = models.Message(
        conversation_id=conversation.id,
        role=models.MessageRole.ASSISTANT,
        content=response
    )
    db.add(assistant_msg)
    conversation.updated_at = datetime.utcnow()
    db.commit()
    return response

def generate_response(user_message: str) -> str:
    """
    Генерирует ответ на основе сообщения пользователя.
    Пока используем простые правила.
    """
    user_message_lower = user_message.lower()
    if "привет" in user_message_lower or "здравствуй" in user_message_lower:
        return "Привет! Я твой персональный ассистент Джарвис. Чем могу помочь?"
    elif "как дела" in user_message_lower:
        return "У меня всё отлично! Надеюсь, у тебя тоже. Расскажи, как продвигаются твои цели?"
    elif "помощь" in user_message_lower or "help" in user_message_lower:
        return "Я могу помочь тебе с привычками, целями, дать статистику или просто поддержать. Что именно тебя интересует?"
    elif "пока" in user_message_lower or "до свидания" in user_message_lower:
        return "До встречи! Удачи в достижении целей."
    else:
        return "Я тебя понял. Давай продолжим работу над твоими целями."
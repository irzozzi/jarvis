from uuid import UUID
from datetime import datetime
from .. import models
from . import intent_classifier
from .response_generator import ResponseGenerator
from ..core.database import SessionLocal

def process_message(user_id: UUID, message: str) -> str:
    db = SessionLocal()
    try:
        # Определяем интент
        intent, _ = intent_classifier.classify_intent(message)

        # Генерируем персонализированный ответ
        generator = ResponseGenerator(db, user_id)
        response = generator.generate_response(intent, message)

        # Сохраняем сообщение пользователя и ответ ассистента
        conversation = (
            db.query(models.Conversation)
            .filter(models.Conversation.user_id == user_id)
            .order_by(models.Conversation.updated_at.desc())
            .first()
        )
        if not conversation:
            conversation = models.Conversation(user_id=user_id)
            db.add(conversation)
            db.flush()

        user_msg = models.Message(
            conversation_id=conversation.id,
            role=models.MessageRole.USER,
            content=message,
        )
        assistant_msg = models.Message(
            conversation_id=conversation.id,
            role=models.MessageRole.ASSISTANT,
            content=response,
        )

        db.add(user_msg)
        db.add(assistant_msg)
        conversation.updated_at = datetime.utcnow()
        db.commit()
        return response
    finally:
        db.close()

from uuid import UUID
from typing import Dict, Any
from sqlalchemy.orm import Session
from .. import models
from . import stats as stats_service

class ResponseGenerator:
    """
    Генератор ответов для ассистента. Собирает данные пользователя и формирует
    персонализированный ответ на основе интента.
    """
    
    def __init__(self, db: Session, user_id: UUID):
        self.db = db
        self.user_id = user_id
        self.user = db.query(models.User).filter(models.User.id == user_id).first()
        self.personality = db.query(models.Personality).filter(
            models.Personality.user_id == user_id
        ).first()
    
    def _get_stats_summary(self) -> str:
        """Собирает краткую сводку по привычкам"""
        habits = self.db.query(models.Habit).filter(
            models.Habit.user_id == self.user_id
        ).all()
        if not habits:
            return "У тебя пока нет привычек."
        
        total_habits = len(habits)
        active_habits = sum(1 for h in habits if h.is_active)

        habit_ids = [h.id for h in habits]
        logs = (
            self.db.query(models.HabitLog)
            .filter(models.HabitLog.habit_id.in_(habit_ids))
            .order_by(models.HabitLog.completed_at.desc())
            .all()
        )
        logs_by_habit: dict[UUID, list[models.HabitLog]] = {}
        for log in logs:
            logs_by_habit.setdefault(log.habit_id, []).append(log)

        total_logs = len(logs)
        streaks = [stats_service.calculate_streak(logs_by_habit.get(h.id, [])) for h in habits]
        
        avg_streak = sum(streaks) / len(streaks) if streaks else 0
        max_streak = max(streaks) if streaks else 0
        
        return (f"У тебя {total_habits} привычек, из них {active_habits} активных. "
                f"Всего {total_logs} выполнений. Средняя серия: {avg_streak:.1f} дней, "
                f"максимальная: {max_streak} дней.")
    
    def _get_insight_summary(self) -> str:
        """Возвращает последний инсайт"""
        insight = self.db.query(models.Insight).filter(
            models.Insight.user_id == self.user_id,
            models.Insight.is_read == False
        ).order_by(models.Insight.created_at.desc()).first()
        
        if insight:
            return f"Вот интересное наблюдение: {insight.content}"
        return "Пока нет новых инсайтов. Занимайся регулярно, и они появятся."
    
    def _get_goal_summary(self) -> str:
        """Сводка по целям"""
        goals = self.db.query(models.Goal).filter(
            models.Goal.user_id == self.user_id,
            models.Goal.status == "active"
        ).all()
        
        if not goals:
            return "У тебя нет активных целей. Хочешь поставить новую?"
        
        goal_list = "\n".join([f"- {g.title} (прогресс {g.progress}%)" for g in goals[:3]])
        return f"Твои активные цели:\n{goal_list}"
    
    def _get_motivation(self) -> str:
        """Генерирует мотивационное сообщение на основе психотипа"""
        if not self.personality:
            return "Верю в тебя! Ты сможешь достичь своих целей."
        
        ptype = self.personality.type
        if ptype == "достигатор":
            return "Ты уже столько всего достиг! Ещё немного — и ты побьёшь свой рекорд."
        elif ptype == "исследователь":
            return "Каждый день ты узнаёшь что-то новое о себе. Это ценный опыт."
        elif ptype == "чувствительный":
            return "Я понимаю, что иногда бывает трудно. Ты молодец, что продолжаешь."
        else:
            return "Просто сделай маленький шаг сегодня — и гордись собой."
    
    def generate_response(self, intent: str, message: str) -> str:
        """
        Генерирует ответ на основе интента и данных пользователя.
        """
        if intent == "greeting":
            name = "друг"
            if self.user and getattr(self.user, "email", None):
                name = self.user.email.split("@")[0] or name
            return f"Привет, {name}! {self._get_motivation()}"
        
        elif intent == "stats":
            return self._get_stats_summary()
        
        elif intent == "insight":
            return self._get_insight_summary()
        
        elif intent == "motivation":
            return self._get_motivation()
        
        elif intent == "goal":
            return self._get_goal_summary()
        
        elif intent == "habit":
            return ("Твои привычки формируют твоё будущее. "
                    "Можешь посмотреть статистику или спросить про конкретную.")
        
        elif intent == "context":
            return ("Я пока не научился определять контекст, "
                    "но скоро смогу подсказывать погоду и напоминать о делах.")
        
        elif intent == "help":
            return ("Я умею:\n"
                    "- показывать статистику привычек\n"
                    "- давать инсайты и советы\n"
                    "- мотивировать\n"
                    "- помогать с целями\n"
                    "- просто поддерживать разговор\n\n"
                    "Что тебя интересует?")
        
        elif intent == "farewell":
            return "До встречи! Возвращайся, чтобы продолжить путь к своим целям."
        
        else:
            return ("Я тебя понял. Расскажи подробнее, что ты хочешь? "
                    "Я могу помочь с привычками, целями, дать статистику или просто поддержать.")
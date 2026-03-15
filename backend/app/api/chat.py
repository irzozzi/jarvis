import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID

from ..core.database import SessionLocal
from .. import schemas, models
from ..api import deps
from ..services import chat_service

# Настройка логгера для этого модуля
logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[UUID, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: UUID):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: UUID):
        self.active_connections.pop(user_id, None)

    async def send_message(self, message: str, user_id: UUID):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    # Аутентификация по токену
    try:
        user = await deps.get_current_user(token=token, db=db)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, user.id)
    try:
        while True:
            data = await websocket.receive_text()
            # Обработка входящего сообщения
            response = await chat_service.process_message(user.id, data, db)
            await manager.send_message(response, user.id)
    except WebSocketDisconnect:
        manager.disconnect(user.id)
    except Exception as e:
        # Логируем ошибку с помощью настроенного логгера
        logger.error(f"WebSocket error for user {user.id}: {e}")
        manager.disconnect(user.id)
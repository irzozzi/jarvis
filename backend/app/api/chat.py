import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from uuid import UUID
from jose import JWTError, jwt
from starlette.concurrency import run_in_threadpool

from ..core.database import SessionLocal
from ..core.security import SECRET_KEY, ALGORITHM
from .. import schemas, models
from ..services import chat_service

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

def _authenticate_user(token: str) -> models.User | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
        user_uuid = UUID(str(user_id))
    except (JWTError, ValueError):
        return None

    db = SessionLocal()
    try:
        return db.query(models.User).filter(models.User.id == user_uuid).first()
    finally:
        db.close()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
):
    user = await run_in_threadpool(_authenticate_user, token)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, user.id)
    try:
        while True:
            data = await websocket.receive_text()
            # Вызываем асинхронную функцию напрямую
            response = await chat_service.process_message(user.id, data)
            await manager.send_message(response, user.id)
    except WebSocketDisconnect:
        manager.disconnect(user.id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user.id}: {e}")
        manager.disconnect(user.id)
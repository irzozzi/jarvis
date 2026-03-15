from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class MessageBase(BaseModel):
    role: MessageRole
    content: str

class MessageCreate(MessageBase):
    conversation_id: UUID

class MessageOut(MessageBase):
    id: UUID
    conversation_id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ConversationBase(BaseModel):
    pass

class ConversationCreate(ConversationBase):
    pass

class ConversationOut(ConversationBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    messages: List[MessageOut] = []
    model_config = ConfigDict(from_attributes=True)
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MessageRequest(BaseModel):
    content: str


class Message(BaseModel):
    id: UUID
    sender: str
    content: str
    timestamp: datetime


class MessageHistoryResponse(BaseModel):
    messages: list[Message]

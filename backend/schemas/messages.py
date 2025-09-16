from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class MessageRequest(BaseModel):
    content: str = Field(..., min_length=1, strip_whitespace=True)

class Message(BaseModel):
    id: UUID
    sender: str
    content: str
    timestamp: datetime

class MessageHistoryResponse(BaseModel):
    messages: list[Message]

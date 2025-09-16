from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class MessageRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    content: str = Field(min_length=1)

class Message(BaseModel):
    id: UUID
    sender: str
    content: str
    timestamp: datetime

class MessageHistoryResponse(BaseModel):
    messages: list[Message]

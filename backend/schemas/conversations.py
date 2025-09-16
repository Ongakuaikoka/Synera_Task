from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class ConversationSummary(BaseModel):
    id: UUID
    created_at: datetime
    last_activity_at: datetime | None = None
    title: str | None = None

class ConversationsResponse(BaseModel):
    conversations: list[ConversationSummary]

class ConversationCreateResponse(BaseModel):
    id: UUID
    title: str | None = None

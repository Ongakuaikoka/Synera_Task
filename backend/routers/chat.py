import asyncio
import logging
from asyncio import QueueEmpty
from datetime import datetime, timezone
from typing import Dict
from uuid import UUID, uuid4

from fastapi import APIRouter, WebSocket, HTTPException, status
from starlette.websockets import WebSocketDisconnect

from infrastructure.llm_client import invoke_llm
from schemas.messages import MessageRequest, MessageHistoryResponse, Message
from schemas.conversations import (
    ConversationCreateResponse,
    ConversationsResponse,
    ConversationSummary,
)

_logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat")

# In-memory store
_message_histories: Dict[UUID, list[Message]] = {}
_notification_queues: Dict[UUID, asyncio.Queue[Message]] = {}
_conversation_meta: Dict[UUID, ConversationSummary] = {}

def _ensure_conversation(conv_id: UUID) -> None:
    if conv_id not in _message_histories:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

def _touch(conv_id: UUID, ts: datetime) -> None: 
    meta = _conversation_meta.get(conv_id)
    if meta:
        meta.last_activity_at = ts

def _derive_title(text: str, max_len: int = 40) -> str:
    first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    if len(first) > max_len:
        first = first[: max_len - 1].rstrip() + "…"
    return first or "Conversation"

@router.post("/conversations", response_model=ConversationCreateResponse, status_code=201)
def create_conversation() -> ConversationCreateResponse:
    conv_id = uuid4()
    _message_histories[conv_id] = []
    _notification_queues[conv_id] = asyncio.Queue()
    _conversation_meta[conv_id] = ConversationSummary(
        id=conv_id, created_at=datetime.now(timezone.utc), title=None
    )
    _logger.info("Created conversation %s", conv_id)
    return ConversationCreateResponse(id=conv_id, title=None)

@router.get("/conversations", response_model=ConversationsResponse)
def list_conversations() -> ConversationsResponse:
    def last_ts(s: ConversationSummary):
        return s.last_activity_at or s.created_at
    items = sorted(_conversation_meta.values(), key=last_ts, reverse=True)
    return ConversationsResponse(conversations=items)

@router.get("/conversations/{conv_id}/messages", response_model=MessageHistoryResponse)
def get_conversation_history(conv_id: UUID) -> MessageHistoryResponse:
    _ensure_conversation(conv_id)
    return MessageHistoryResponse(messages=_message_histories[conv_id])

@router.post("/conversations/{conv_id}/messages", status_code=202)
async def send_conversation_message(conv_id: UUID, message_request: MessageRequest):
    _ensure_conversation(conv_id)
    _logger.info("Message enqueued for conversation %s", conv_id)
    asyncio.create_task(_process_message(conv_id, message_request.content))

@router.websocket("/conversations/{conv_id}/notifications")
async def subscribe_conversation(ws: WebSocket, conv_id: UUID):
    _ensure_conversation(conv_id)
    await ws.accept()
    _logger.info("WS connected: %s", conv_id)
    queue = _notification_queues[conv_id]
    while True:
        try:
            msg = queue.get_nowait()
            await ws.send_text(msg.model_dump_json())
        except QueueEmpty:
            pass
        try:
            await asyncio.wait_for(ws.receive_text(), 0.1)
        except asyncio.TimeoutError:
            pass
        except WebSocketDisconnect:
            _logger.info("WS disconnected: %s", conv_id)
            break

async def _process_message(conv_id: UUID, content: str) -> None:
    try:
        now = datetime.now(timezone.utc)
        user_msg = Message(id=uuid4(), sender="You", content=content, timestamp=now)
        await _publish_message(conv_id, user_msg)
        _touch(conv_id, now)

        meta = _conversation_meta.get(conv_id)
        if meta and not getattr(meta, "title", None):
            meta.title = _derive_title(content)

        reply = await invoke_llm(content)

        now2 = datetime.now(timezone.utc)
        ai_msg = Message(id=uuid4(), sender="Bob", content=reply, timestamp=now2)
        await _publish_message(conv_id, ai_msg)
        _touch(conv_id, now2)
    except Exception:
        _logger.exception("Background task failed")

async def _publish_message(conv_id: UUID, message: Message) -> None:
    await _notification_queues[conv_id].put(message)
    _message_histories[conv_id].append(message)

import asyncio
import logging
from asyncio import QueueEmpty
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

from infrastructure.llm_client import invoke_llm
from schemas.messages import MessageRequest, MessageHistoryResponse, Message

_logger = logging.getLogger("uvicorn")

router = APIRouter(prefix="/api/chat")

_message_history: list[Message] = []
_notification_queue = asyncio.Queue[Message]()


@router.get("/messages")
def get_message_history() -> MessageHistoryResponse:
    return MessageHistoryResponse(messages=_message_history)


@router.post("/messages", status_code=202)
async def send_message(message_request: MessageRequest):
    _logger.info("Received message from client.")
    # Process the message in the background and return 202 Accepted.
    asyncio.create_task(_process_message(message_request.content))


@router.websocket("/notifications")
async def subscribe(ws: WebSocket):
    await ws.accept()
    _logger.info("Client connected.")
    while True:
        try:
            message = _notification_queue.get_nowait()
            _logger.info("Sending message to client.")
            await ws.send_text(message.model_dump_json())
        except QueueEmpty:
            pass

        # Wait for 100ms before checking the queue again and use receive_text() to check if the client is still connected.
        try:
            await asyncio.wait_for(ws.receive_text(), 0.1)
        except TimeoutError:
            pass
        except WebSocketDisconnect:
            _logger.info("Client disconnected.")
            break


async def _process_message(content: str):
    user_msg = Message(id=uuid4(), sender="You", content=content, timestamp=datetime.now(timezone.utc))
    await _publish_message(user_msg)
    response = await invoke_llm(content)
    ai_msg = Message(id=uuid4(), sender="Bob", content=response, timestamp=datetime.now(timezone.utc))
    await _publish_message(ai_msg)


async def _publish_message(message: Message):
    await _notification_queue.put(message)
    _message_history.append(message)

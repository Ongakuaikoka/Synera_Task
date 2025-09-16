from __future__ import annotations

import json
import uuid
from fastapi.testclient import TestClient

from backend.main import app as fastapi_app
from backend.routers import chat as chat_router



def _reset_state():
    """
    Reset in-memory storage so tests don't leak state between runs.
    Safe even if some attrs don't exist (legacy codepaths removed).
    """
    for name in ("_message_histories", "_notification_queues", "_conversation_meta"):
        dct = getattr(chat_router, name, None)
        if isinstance(dct, dict):
            dct.clear()


def test_create_and_list_conversations():
    _reset_state()
    client = TestClient(fastapi_app)

    r = client.post("/api/chat/conversations")
    assert r.status_code == 201
    data = r.json()
    conv_id = data["id"]
    assert uuid.UUID(conv_id)
    assert "title" in data

    r = client.get("/api/chat/conversations")
    assert r.status_code == 200
    items = r.json()["conversations"]
    assert any(c["id"] == conv_id for c in items)


def test_get_messages_empty_after_create():
    _reset_state()
    client = TestClient(fastapi_app)

    conv_id = client.post("/api/chat/conversations").json()["id"]
    r = client.get(f"/api/chat/conversations/{conv_id}/messages")
    assert r.status_code == 200
    assert r.json() == {"messages": []}


def test_404_unknown_conversation():
    _reset_state()
    client = TestClient(fastapi_app)

    bad = str(uuid.uuid4())
    r = client.get(f"/api/chat/conversations/{bad}/messages")
    assert r.status_code in (404, 422) 
    r = client.post(f"/api/chat/conversations/{bad}/messages", json={"content": "hi"})
    assert r.status_code in (404, 422)


def test_422_bad_uuid_path_param():
    _reset_state()
    client = TestClient(fastapi_app)

    r = client.get("/api/chat/conversations/not-a-uuid/messages")
    assert r.status_code == 422


def test_send_and_stream_messages_over_websocket(monkeypatch):
    """
    Sends a message to a real conversation and asserts we receive:
      1) the user message
      2) the AI reply (mocked)
    over the per-conversation WebSocket stream.
    """
    _reset_state()
    client = TestClient(fastapi_app)

    conv_id = client.post("/api/chat/conversations").json()["id"]

    async def fake_invoke_llm(prompt: str) -> str:
        return f"[AI echo] {prompt}"

    monkeypatch.setattr(
        chat_router, "invoke_llm", fake_invoke_llm, raising=True
    )

    with client.websocket_connect(f"/api/chat/conversations/{conv_id}/notifications") as ws:
        r = client.post(
            f"/api/chat/conversations/{conv_id}/messages",
            json={"content": "Hello there"},
        )
        assert r.status_code == 202

        raw1 = ws.receive_text()
        msg1 = json.loads(raw1)
        assert msg1["sender"] == "You"
        assert msg1["content"] == "Hello there"

        raw2 = ws.receive_text()
        msg2 = json.loads(raw2)
        assert msg2["sender"] == "Bob"
        assert msg2["content"] == "[AI echo] Hello there"


def test_list_sorts_by_last_activity(monkeypatch):
    """
    Creates two conversations, sends a message only to the second,
    verifies the second appears first in /conversations.
    """
    _reset_state()
    client = TestClient(fastapi_app)

    c1 = client.post("/api/chat/conversations").json()["id"]
    c2 = client.post("/api/chat/conversations").json()["id"]

    async def fake_invoke_llm(_: str) -> str:
        return "ok"

    monkeypatch.setattr(chat_router, "invoke_llm", fake_invoke_llm, raising=True)

    r = client.post(f"/api/chat/conversations/{c2}/messages", json={"content": "ping"})
    assert r.status_code == 202

    items = client.get("/api/chat/conversations").json()["conversations"]
    assert len(items) >= 2
    assert items[0]["id"] == c2

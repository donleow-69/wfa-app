"""Tests for the AI chat routes."""

from unittest.mock import AsyncMock, patch

from app.models.chat import ChatMessage
from tests.conftest import create_test_user


async def test_chat_page_requires_auth(client):
    resp = await client.get("/chat/")
    assert resp.status_code == 303


async def test_chat_send_empty_message(auth_client):
    resp = await auth_client.post("/chat/send", json={"message": ""})
    assert resp.status_code == 400


async def test_chat_send_success(auth_client):
    """Mock the Anthropic client so we don't make real API calls."""
    mock_response = AsyncMock()
    mock_response.content = [AsyncMock(text="Hello from the assistant!")]

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    with patch("app.routers.chat._get_client", return_value=mock_client):
        resp = await auth_client.post("/chat/send", json={"message": "What are my rights?"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "assistant"
    assert data["content"] == "Hello from the assistant!"


async def test_chat_history(auth_client, db_session, test_user):
    msg1 = ChatMessage(user_id=test_user.id, role="user", content="Hi")
    db_session.add(msg1)
    await db_session.flush()
    msg2 = ChatMessage(user_id=test_user.id, role="assistant", content="Hello!")
    db_session.add(msg2)
    await db_session.commit()

    resp = await auth_client.get("/chat/history")
    assert resp.status_code == 200
    messages = resp.json()
    assert len(messages) == 2
    roles = {m["role"] for m in messages}
    assert roles == {"user", "assistant"}


async def test_chat_rate_limit_free_user(auth_client, db_session, test_user):
    """Free users are limited to 5 messages/day. The 6th should be rejected."""
    # Insert 5 existing user messages for today
    for i in range(5):
        db_session.add(
            ChatMessage(user_id=test_user.id, role="user", content=f"msg {i}")
        )
    await db_session.commit()

    resp = await auth_client.post("/chat/send", json={"message": "sixth message"})
    assert resp.status_code == 429


async def test_chat_no_rate_limit_subscribed(subscribed_client, db_session, subscribed_user):
    """Subscribed users should not be rate-limited."""
    for i in range(5):
        db_session.add(
            ChatMessage(user_id=subscribed_user.id, role="user", content=f"msg {i}")
        )
    await db_session.commit()

    mock_response = AsyncMock()
    mock_response.content = [AsyncMock(text="Pro answer")]

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    with patch("app.routers.chat._get_client", return_value=mock_client):
        resp = await subscribed_client.post("/chat/send", json={"message": "sixth message"})

    assert resp.status_code == 200

"""Tests for the AI chat routes."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.cost_control import KILL_SWITCH_THRESHOLD_USD, current_month
from app.models.chat import ChatMessage
from app.models.spend import SpendLedger
from tests.conftest import create_test_user


def _mock_response(text="Hello from the assistant!", input_tokens=100, output_tokens=50):
    mock_response = AsyncMock()
    mock_response.content = [AsyncMock(text=text)]
    mock_response.usage = SimpleNamespace(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_creation_input_tokens=0,
        cache_read_input_tokens=0,
    )
    return mock_response


async def test_chat_page_requires_auth(client):
    resp = await client.get("/chat/")
    assert resp.status_code == 303


async def test_chat_send_empty_message(auth_client):
    resp = await auth_client.post("/chat/send", json={"message": ""})
    assert resp.status_code == 400


async def test_chat_send_success(auth_client):
    """Mock the Anthropic client so we don't make real API calls."""
    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=_mock_response())

    with patch("app.routers.chat._get_client", return_value=mock_client):
        resp = await auth_client.post("/chat/send", json={"message": "What are my rights?"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "assistant"
    assert data["content"] == "Hello from the assistant!"


async def test_chat_free_tier_uses_haiku_with_cached_system_prompt(auth_client):
    """Free users are routed to the cheap model with a capped max_tokens and a
    cache_control breakpoint on the system prompt."""
    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=_mock_response())

    with patch("app.routers.chat._get_client", return_value=mock_client):
        resp = await auth_client.post("/chat/send", json={"message": "What are my rights?"})

    assert resp.status_code == 200
    _, kwargs = mock_client.messages.create.call_args
    from app.cost_control import FREE_TIER_MAX_TOKENS, FREE_TIER_MODEL

    assert kwargs["model"] == FREE_TIER_MODEL
    assert kwargs["max_tokens"] == FREE_TIER_MAX_TOKENS
    assert kwargs["system"][0]["cache_control"] == {"type": "ephemeral"}


async def test_chat_subscribed_uses_paid_model(subscribed_client):
    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=_mock_response("Pro answer"))

    with patch("app.routers.chat._get_client", return_value=mock_client):
        resp = await subscribed_client.post("/chat/send", json={"message": "What are my rights?"})

    assert resp.status_code == 200
    _, kwargs = mock_client.messages.create.call_args
    from app.routers.chat import PAID_TIER_MAX_TOKENS, PAID_TIER_MODEL

    assert kwargs["model"] == PAID_TIER_MODEL
    assert kwargs["max_tokens"] == PAID_TIER_MAX_TOKENS


async def test_chat_send_records_spend(auth_client, db_session):
    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=_mock_response(input_tokens=1000, output_tokens=1000))

    with patch("app.routers.chat._get_client", return_value=mock_client):
        resp = await auth_client.post("/chat/send", json={"message": "What are my rights?"})

    assert resp.status_code == 200
    result = await db_session.execute(
        SpendLedger.__table__.select().where(SpendLedger.month == current_month())
    )
    row = result.first()
    assert row is not None
    # Haiku: 1000 input tokens @ $1/MTok + 1000 output tokens @ $5/MTok
    assert row.spend_usd > 0


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

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=_mock_response("Pro answer"))

    with patch("app.routers.chat._get_client", return_value=mock_client):
        resp = await subscribed_client.post("/chat/send", json={"message": "sixth message"})

    assert resp.status_code == 200


async def test_chat_quota_free_user(auth_client, db_session, test_user):
    db_session.add(ChatMessage(user_id=test_user.id, role="user", content="msg"))
    await db_session.commit()

    resp = await auth_client.get("/chat/quota")
    assert resp.status_code == 200
    data = resp.json()
    assert data["unlimited"] is False
    assert data["limit"] == 5
    assert data["used"] == 1
    assert data["remaining"] == 4


async def test_chat_quota_subscribed_unlimited(subscribed_client):
    resp = await subscribed_client.get("/chat/quota")
    assert resp.status_code == 200
    assert resp.json() == {"unlimited": True}


async def test_chat_kill_switch_blocks_free_tier(auth_client, db_session):
    """Once month-to-date spend hits the threshold, free users get a graceful
    'capacity reached' message and the Anthropic API is not called."""
    db_session.add(SpendLedger(month=current_month(), spend_usd=KILL_SWITCH_THRESHOLD_USD))
    await db_session.commit()

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=_mock_response())

    with patch("app.routers.chat._get_client", return_value=mock_client):
        resp = await auth_client.post("/chat/send", json={"message": "What are my rights?"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["capacity_reached"] is True
    mock_client.messages.create.assert_not_called()


async def test_chat_kill_switch_bypassed_for_subscribed(subscribed_client, db_session):
    """Paid users bypass the kill switch even when the free-tier cap is reached."""
    db_session.add(SpendLedger(month=current_month(), spend_usd=KILL_SWITCH_THRESHOLD_USD))
    await db_session.commit()

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=_mock_response("Pro answer"))

    with patch("app.routers.chat._get_client", return_value=mock_client):
        resp = await subscribed_client.post("/chat/send", json={"message": "What are my rights?"})

    assert resp.status_code == 200
    data = resp.json()
    assert data.get("content") == "Pro answer"
    mock_client.messages.create.assert_called_once()

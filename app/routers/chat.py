"""Chat with Claude about workplace fairness topics."""

import os
from datetime import date

import anthropic
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select

from ..auth import get_current_user
from ..cost_control import FREE_TIER_MAX_TOKENS, FREE_TIER_MODEL, kill_switch_active, record_spend
from ..database import get_db
from ..limiter import limiter, user_or_ip_key
from ..models.chat import ChatMessage
from ..models.user import User

router = APIRouter(prefix="/chat")
templates = Jinja2Templates(directory="app/templates")

FREE_DAILY_MESSAGES = 5

PAID_TIER_MODEL = "claude-sonnet-4-6"
PAID_TIER_MAX_TOKENS = 1024

FREE_CAPACITY_MESSAGE = (
    "We've reached our free chat capacity for this month. Free access resumes next month — "
    "upgrade to Pro for uninterrupted access."
)

SYSTEM_PROMPT = (
    "You are a helpful workplace fairness assistant. You help employees and employers "
    "understand their rights and obligations under employment law. You cover topics such as "
    "anti-discrimination, wages, workplace safety, leave, harassment, compliance, and labour "
    "relations across the United States, Singapore, Malaysia, Indonesia, the Philippines, and Thailand.\n\n"
    "Important rules:\n"
    "- Only answer questions related to workplace fairness, employment law, and labour rights.\n"
    "- If a question is unrelated to workplace fairness, politely decline and redirect the user.\n"
    "- Provide general information only — always remind users that this is not legal advice.\n"
    "- Be concise but thorough. Use bullet points where helpful.\n"
    "- If you are unsure, say so rather than guessing."
)

# Cached as a content block: identical on every call, so repeated requests hit the
# prompt cache instead of reprocessing the system prompt (see cost_control.py).
SYSTEM_PROMPT_BLOCKS = [{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}]


def _get_client() -> anthropic.AsyncAnthropic:
    return anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))


async def _daily_message_count(db, user_id: int) -> int:
    today = date.today().isoformat()
    result = await db.execute(
        select(func.count())
        .select_from(ChatMessage)
        .where(
            ChatMessage.user_id == user_id,
            ChatMessage.role == "user",
            func.date(ChatMessage.created_at) == today,
        )
    )
    return result.scalar() or 0


@router.get("/", response_class=HTMLResponse)
async def chat_page(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse(request, "chat.html", {"user": user})


@router.get("/history", response_class=JSONResponse)
async def chat_history(user: User = Depends(get_current_user), db=Depends(get_db)):
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(20)
    )
    messages = list(reversed(result.scalars().all()))
    return [{"role": m.role, "content": m.content} for m in messages]


@router.get("/quota", response_class=JSONResponse)
async def chat_quota(user: User = Depends(get_current_user), db=Depends(get_db)):
    """Remaining free daily messages for the signed-in user (unlimited for subscribers)."""
    if user.is_subscribed:
        return {"unlimited": True}
    used = await _daily_message_count(db, user.id)
    return {
        "unlimited": False,
        "limit": FREE_DAILY_MESSAGES,
        "used": used,
        "remaining": max(0, FREE_DAILY_MESSAGES - used),
    }


@router.post("/send", response_class=JSONResponse)
@limiter.limit("20/minute")
@limiter.limit("8/minute", key_func=user_or_ip_key)
async def chat_send(request: Request, user: User = Depends(get_current_user), db=Depends(get_db)):
    body = await request.json()
    user_message = (body.get("message") or "").strip()
    if not user_message:
        return JSONResponse({"error": "Message cannot be empty."}, status_code=400)

    is_free_tier = not user.is_subscribed

    if is_free_tier:
        # Per-user daily quota, tracked server-side by user id.
        daily_count = await _daily_message_count(db, user.id)
        if daily_count >= FREE_DAILY_MESSAGES:
            return JSONResponse(
                {"error": f"Daily message limit reached ({FREE_DAILY_MESSAGES}). Upgrade to Pro for unlimited chat."},
                status_code=429,
            )

        # Global spend kill switch — paid users bypass this.
        if await kill_switch_active(db):
            return JSONResponse(
                {"role": "assistant", "content": FREE_CAPACITY_MESSAGE, "capacity_reached": True}
            )

    # Save user message
    user_msg = ChatMessage(user_id=user.id, role="user", content=user_message)
    db.add(user_msg)
    await db.flush()

    # Build context from last 20 messages
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(20)
    )
    history = list(reversed(result.scalars().all()))
    api_messages = [{"role": m.role, "content": m.content} for m in history]

    model = FREE_TIER_MODEL if is_free_tier else PAID_TIER_MODEL
    max_tokens = FREE_TIER_MAX_TOKENS if is_free_tier else PAID_TIER_MAX_TOKENS

    # Call Claude
    try:
        client = _get_client()
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=SYSTEM_PROMPT_BLOCKS,
            messages=api_messages,
        )
        assistant_text = response.content[0].text
        await record_spend(db, model, response.usage)
    except Exception as exc:
        await db.rollback()
        return JSONResponse({"error": f"AI service error: {exc}"}, status_code=502)

    # Save assistant response
    assistant_msg = ChatMessage(user_id=user.id, role="assistant", content=assistant_text)
    db.add(assistant_msg)
    await db.commit()

    return {"role": "assistant", "content": assistant_text}

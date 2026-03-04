"""Chat with Claude about workplace fairness topics."""

import os
from datetime import date

import anthropic
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select

from ..auth import get_current_user
from ..database import get_db
from ..models.chat import ChatMessage
from ..models.user import User

router = APIRouter(prefix="/chat")
templates = Jinja2Templates(directory="app/templates")

FREE_DAILY_MESSAGES = 5

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


def _get_client() -> anthropic.AsyncAnthropic:
    return anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))


@router.get("/", response_class=HTMLResponse)
async def chat_page(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("chat.html", {"request": request, "user": user})


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


@router.post("/send", response_class=JSONResponse)
async def chat_send(request: Request, user: User = Depends(get_current_user), db=Depends(get_db)):
    body = await request.json()
    user_message = (body.get("message") or "").strip()
    if not user_message:
        return JSONResponse({"error": "Message cannot be empty."}, status_code=400)

    # Rate limiting for free users
    if not user.is_subscribed:
        today = date.today().isoformat()
        count_result = await db.execute(
            select(func.count())
            .select_from(ChatMessage)
            .where(
                ChatMessage.user_id == user.id,
                ChatMessage.role == "user",
                func.date(ChatMessage.created_at) == today,
            )
        )
        daily_count = count_result.scalar() or 0
        if daily_count >= FREE_DAILY_MESSAGES:
            return JSONResponse(
                {"error": f"Daily message limit reached ({FREE_DAILY_MESSAGES}). Upgrade to Pro for unlimited chat."},
                status_code=429,
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

    # Call Claude
    try:
        client = _get_client()
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=api_messages,
        )
        assistant_text = response.content[0].text
    except Exception as exc:
        await db.rollback()
        return JSONResponse({"error": f"AI service error: {exc}"}, status_code=502)

    # Save assistant response
    assistant_msg = ChatMessage(user_id=user.id, role="assistant", content=assistant_text)
    db.add(assistant_msg)
    await db.commit()

    return {"role": "assistant", "content": assistant_text}

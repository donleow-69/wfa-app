"""Contract checker — AI-powered employment contract analysis."""

import io
import json
import os
from datetime import date

import anthropic
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select

from ..auth import get_current_user
from ..cost_control import FREE_TIER_MODEL, record_spend
from ..database import get_db
from ..models.contract_check import ContractCheck
from ..models.user import User
from .policies import COUNTRY_NAMES

router = APIRouter(prefix="/contract-checker")
templates = Jinja2Templates(directory="app/templates")

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
MAX_CHARS = 50_000
FREE_DAILY_CHECKS = 3
PAID_MODEL = "claude-sonnet-4-6"
PAID_MAX_TOKENS = 4096
FREE_MAX_TOKENS = 1500


def _get_client() -> anthropic.AsyncAnthropic:
    return anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))


def _extract_text_from_pdf(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n".join(parts)


def _extract_text_from_docx(data: bytes) -> str:
    from docx import Document

    doc = Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


async def _extract_text_from_upload(file: UploadFile) -> str:
    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise ValueError("File exceeds 2 MB limit.")

    filename = (file.filename or "").lower()
    if filename.endswith(".pdf"):
        text = _extract_text_from_pdf(data)
    elif filename.endswith(".docx"):
        text = _extract_text_from_docx(data)
    else:
        raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")

    if not text.strip():
        raise ValueError("Could not extract text from the uploaded file.")
    return text[:MAX_CHARS]


async def _daily_check_count(db, user_id: int) -> int:
    today = date.today().isoformat()
    result = await db.execute(
        select(func.count())
        .select_from(ContractCheck)
        .where(
            ContractCheck.user_id == user_id,
            func.date(ContractCheck.created_at) == today,
        )
    )
    return result.scalar() or 0


def _build_prompt(contract_text: str, country: str, is_free: bool) -> str:
    country_name = COUNTRY_NAMES.get(country, "United States")
    depth = (
        "Focus on clearly illegal clauses and obviously missing mandatory provisions only."
        if is_free
        else "Provide a thorough analysis including illegal clauses, missing provisions, red flags, and recommendations."
    )

    return (
        f"You are an employment law specialist. Analyze the following employment contract "
        f"against {country_name} employment law requirements.\n\n"
        f"{depth}\n\n"
        f"## Contract Text\n"
        f"{contract_text}\n\n"
        f"## Instructions\n"
        f"Return a JSON object (no markdown fences) with this exact structure:\n"
        f"{{\n"
        f'  "contract_type": "string identifying the contract type",\n'
        f'  "risk_score": <number 0-100, higher = more risk for the employee>,\n'
        f'  "summary": "Brief overall assessment",\n'
        f'  "illegal_clauses": [\n'
        f'    {{"clause": "quoted or paraphrased clause", "issue": "why it is illegal/unenforceable", "severity": "high|medium|low"}}\n'
        f'  ],\n'
        f'  "missing_provisions": [\n'
        f'    {{"provision": "what is missing", "requirement": "legal basis", "severity": "high|medium|low"}}\n'
        f'  ],\n'
        f'  "red_flags": [\n'
        f'    {{"clause": "quoted or paraphrased clause", "concern": "why this is unfair or one-sided", "severity": "high|medium|low"}}\n'
        f'  ],\n'
        f'  "recommendations": [\n'
        f'    {{"priority": 1, "action": "specific action to take"}}\n'
        f'  ]\n'
        f"}}\n\n"
        f"Return ONLY valid JSON. No markdown, no extra text."
    )


def _parse_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return json.loads(cleaned.strip())


@router.get("/", response_class=HTMLResponse)
async def checker_form(request: Request, user: User = Depends(get_current_user), db=Depends(get_db)):
    remaining = None
    if not user.is_subscribed:
        used = await _daily_check_count(db, user.id)
        remaining = max(0, FREE_DAILY_CHECKS - used)
    return templates.TemplateResponse(
        request,
        "contract_checker.html",
        {"user": user, "countries": COUNTRY_NAMES, "remaining": remaining},
    )


@router.post("/analyze", response_class=HTMLResponse)
async def analyze_contract(
    request: Request,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
    country: str = Form("us"),
    contract_text: str = Form(""),
    file: UploadFile | None = File(None),
):
    is_free = not user.is_subscribed

    if is_free:
        used = await _daily_check_count(db, user.id)
        if used >= FREE_DAILY_CHECKS:
            remaining = 0
            return templates.TemplateResponse(
                request,
                "contract_checker.html",
                {
                    "user": user,
                    "countries": COUNTRY_NAMES,
                    "remaining": remaining,
                    "error": f"Daily limit reached ({FREE_DAILY_CHECKS} checks/day). Upgrade to Pro for unlimited access.",
                },
                status_code=429,
            )

    # Extract text
    text = ""
    error = None
    if file and file.filename:
        try:
            text = await _extract_text_from_upload(file)
        except ValueError as e:
            error = str(e)
        except Exception:
            error = "Failed to process the uploaded file."
    else:
        text = contract_text.strip()

    if not text and not error:
        error = "Please paste contract text or upload a PDF or DOCX file."

    if error:
        remaining = None if not is_free else max(0, FREE_DAILY_CHECKS - (await _daily_check_count(db, user.id)))
        return templates.TemplateResponse(
            request,
            "contract_checker.html",
            {"user": user, "countries": COUNTRY_NAMES, "remaining": remaining, "error": error},
            status_code=400,
        )

    text = text[:MAX_CHARS]
    model = FREE_TIER_MODEL if is_free else PAID_MODEL
    max_tokens = FREE_MAX_TOKENS if is_free else PAID_MAX_TOKENS

    prompt = _build_prompt(text, country, is_free)
    try:
        client = _get_client()
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        await record_spend(db, model, response.usage)
        analysis = _parse_json(response.content[0].text)
    except json.JSONDecodeError:
        error = "Failed to parse the analysis results. Please try again."
        remaining = None if not is_free else max(0, FREE_DAILY_CHECKS - (await _daily_check_count(db, user.id)))
        return templates.TemplateResponse(
            request,
            "contract_checker.html",
            {"user": user, "countries": COUNTRY_NAMES, "remaining": remaining, "error": error},
            status_code=502,
        )
    except Exception as exc:
        error = f"AI service error: {exc}"
        remaining = None if not is_free else max(0, FREE_DAILY_CHECKS - (await _daily_check_count(db, user.id)))
        return templates.TemplateResponse(
            request,
            "contract_checker.html",
            {"user": user, "countries": COUNTRY_NAMES, "remaining": remaining, "error": error},
            status_code=502,
        )

    # Record usage after successful check
    db.add(ContractCheck(user_id=user.id))
    await db.commit()

    country_name = COUNTRY_NAMES.get(country, "United States")
    remaining_after = None
    if is_free:
        new_count = await _daily_check_count(db, user.id)
        remaining_after = max(0, FREE_DAILY_CHECKS - new_count)

    return templates.TemplateResponse(
        request,
        "contract_checker_result.html",
        {
            "user": user,
            "analysis": analysis,
            "country_name": country_name,
            "is_free": is_free,
            "remaining": remaining_after,
        },
    )

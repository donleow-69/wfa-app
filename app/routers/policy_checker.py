"""Policy compliance checker — AI-powered gap analysis for workplace policies."""

import io
import json
import os

import anthropic
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..auth import get_current_user
from ..models.user import User
from .compliance import DEFAULT_ITEMS_BY_COUNTRY
from .policies import COUNTRY_NAMES

router = APIRouter(prefix="/policy-checker")
templates = Jinja2Templates(directory="app/templates")

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
MAX_CHARS = 50_000


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


def _build_analysis_prompt(policy_text: str, country: str) -> str:
    items = DEFAULT_ITEMS_BY_COUNTRY.get(country, DEFAULT_ITEMS_BY_COUNTRY["us"])
    country_name = COUNTRY_NAMES.get(country, "United States")

    requirements_list = "\n".join(
        f"- [{item['category']}] {item['requirement']}: {item['description']}"
        for item in items
    )

    return (
        f"You are a workplace compliance analyst. Analyze the following workplace policy "
        f"against {country_name} compliance requirements.\n\n"
        f"## Compliance Requirements for {country_name}\n"
        f"{requirements_list}\n\n"
        f"## Policy Text\n"
        f"{policy_text}\n\n"
        f"## Instructions\n"
        f"Analyze the policy and return a JSON object (no markdown fences) with this exact structure:\n"
        f'{{\n'
        f'  "policy_type": "string identifying the type of policy",\n'
        f'  "overall_score": <number 0-100 indicating compliance coverage>,\n'
        f'  "covered": [\n'
        f'    {{"requirement": "...", "category": "...", "assessment": "..."}}\n'
        f'  ],\n'
        f'  "gaps": [\n'
        f'    {{"requirement": "...", "category": "...", "severity": "high|medium|low", "explanation": "..."}}\n'
        f'  ],\n'
        f'  "recommendations": [\n'
        f'    {{"priority": 1, "action": "...", "rationale": "..."}}\n'
        f'  ],\n'
        f'  "summary": "Brief overall summary of the analysis"\n'
        f'}}\n\n'
        f"Return ONLY valid JSON. No markdown, no extra text."
    )


def _parse_json_response(text: str) -> dict:
    """Parse JSON from Claude response, stripping markdown fences if present."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # Remove opening fence (e.g. ```json)
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return json.loads(cleaned.strip())


@router.get("/", response_class=HTMLResponse)
async def checker_form(request: Request, user: User = Depends(get_current_user)):
    if not user.is_subscribed:
        return RedirectResponse("/subscribe", status_code=303)
    return templates.TemplateResponse(
        "policy_checker.html",
        {
            "request": request,
            "user": user,
            "countries": COUNTRY_NAMES,
        },
    )


@router.post("/analyze", response_class=HTMLResponse)
async def analyze_policy(
    request: Request,
    user: User = Depends(get_current_user),
    country: str = Form("us"),
    policy_text: str = Form(""),
    file: UploadFile | None = File(None),
):
    if not user.is_subscribed:
        return RedirectResponse("/subscribe", status_code=303)

    # Extract text from upload or use pasted text
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
        text = policy_text.strip()

    if not text and not error:
        error = "Please paste policy text or upload a PDF/DOCX file."

    if error:
        return templates.TemplateResponse(
            "policy_checker.html",
            {
                "request": request,
                "user": user,
                "countries": COUNTRY_NAMES,
                "error": error,
            },
            status_code=400,
        )

    # Truncate if too long
    text = text[:MAX_CHARS]

    # Call Claude for analysis
    prompt = _build_analysis_prompt(text, country)
    try:
        client = _get_client()
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        result_text = response.content[0].text
        analysis = _parse_json_response(result_text)
    except json.JSONDecodeError:
        error = "Failed to parse the analysis results. Please try again."
        return templates.TemplateResponse(
            "policy_checker.html",
            {
                "request": request,
                "user": user,
                "countries": COUNTRY_NAMES,
                "error": error,
            },
            status_code=502,
        )
    except Exception as exc:
        error = f"AI service error: {exc}"
        return templates.TemplateResponse(
            "policy_checker.html",
            {
                "request": request,
                "user": user,
                "countries": COUNTRY_NAMES,
                "error": error,
            },
            status_code=502,
        )

    country_name = COUNTRY_NAMES.get(country, "United States")
    return templates.TemplateResponse(
        "policy_checker_result.html",
        {
            "request": request,
            "user": user,
            "analysis": analysis,
            "country_name": country_name,
        },
    )

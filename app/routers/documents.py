"""Document generator — AI-drafted employment documents (Pro only)."""

import os

import anthropic
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..auth import get_current_user
from ..cost_control import record_spend
from ..database import get_db
from ..models.user import User
from .policies import COUNTRY_NAMES

router = APIRouter(prefix="/documents")
templates = Jinja2Templates(directory="app/templates")

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 2048

DOCUMENT_TYPES = {
    "resignation": {
        "title": "Resignation Letter",
        "description": "A professional resignation letter with correct notice period references.",
        "audience": "employee",
    },
    "warning": {
        "title": "Warning Letter",
        "description": "A formal written warning or performance improvement plan letter.",
        "audience": "employer",
    },
    "termination": {
        "title": "Termination Letter",
        "description": "A termination letter with mandatory statutory elements for your country.",
        "audience": "employer",
    },
    "investigation": {
        "title": "Investigation Report",
        "description": "A structured workplace investigation report documenting findings and outcome.",
        "audience": "employer",
    },
}


def _get_client() -> anthropic.AsyncAnthropic:
    return anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))


def _build_resignation_prompt(country: str, data: dict) -> str:
    country_name = COUNTRY_NAMES.get(country, "United States")
    return (
        f"Draft a professional resignation letter for an employee in {country_name}.\n\n"
        f"Details:\n"
        f"- Employee name: {data['employee_name']}\n"
        f"- Job title: {data['job_title']}\n"
        f"- Company name: {data['company_name']}\n"
        f"- Manager name: {data['manager_name']}\n"
        f"- Notice period: {data['notice_period']}\n"
        f"- Last working day: {data['last_working_day']}\n"
        f"- Reason (optional): {data.get('reason') or 'personal reasons'}\n\n"
        f"Write a complete, professional resignation letter. Use formal business letter format. "
        f"Reference the statutory notice period requirements under {country_name} employment law if relevant. "
        f"Keep it concise and professional. Output the letter text only — no preamble or explanation."
    )


def _build_warning_prompt(country: str, data: dict) -> str:
    country_name = COUNTRY_NAMES.get(country, "United States")
    return (
        f"Draft a formal written warning letter for an employer in {country_name}.\n\n"
        f"Details:\n"
        f"- Employee name: {data['employee_name']}\n"
        f"- Job title: {data['job_title']}\n"
        f"- Company name: {data['company_name']}\n"
        f"- Manager/issuer name: {data['manager_name']}\n"
        f"- Date of incident: {data['incident_date']}\n"
        f"- Description of issue: {data['incident_description']}\n"
        f"- Previous warnings: {data.get('previous_warnings') or 'None'}\n"
        f"- Improvement required: {data['improvement_required']}\n"
        f"- Improvement deadline: {data['improvement_deadline']}\n\n"
        f"Write a formal written warning letter that complies with {country_name} employment law. "
        f"Include: clear statement of the issue, reference to any prior warnings, specific improvement requirements, "
        f"consequences if improvement is not achieved, and employee's right to respond. "
        f"Use formal business letter format. Output the letter text only — no preamble or explanation."
    )


def _build_termination_prompt(country: str, data: dict) -> str:
    country_name = COUNTRY_NAMES.get(country, "United States")
    return (
        f"Draft a termination letter for an employer in {country_name}.\n\n"
        f"Details:\n"
        f"- Employee name: {data['employee_name']}\n"
        f"- Job title: {data['job_title']}\n"
        f"- Company name: {data['company_name']}\n"
        f"- Manager/issuer name: {data['manager_name']}\n"
        f"- Termination date: {data['termination_date']}\n"
        f"- Reason for termination: {data['termination_reason']}\n"
        f"- Notice period or payment in lieu: {data['notice_details']}\n"
        f"- Final pay date: {data.get('final_pay_date') or 'per statutory requirements'}\n\n"
        f"Write a termination letter that complies with {country_name} employment law. "
        f"Include all mandatory statutory elements (notice, final pay, statutory entitlements). "
        f"Reference relevant legislation where appropriate. Use formal business letter format. "
        f"Output the letter text only — no preamble or explanation."
    )


def _build_investigation_prompt(country: str, data: dict) -> str:
    country_name = COUNTRY_NAMES.get(country, "United States")
    return (
        f"Draft a workplace investigation report for an employer in {country_name}.\n\n"
        f"Details:\n"
        f"- Company name: {data['company_name']}\n"
        f"- Investigator name: {data['investigator_name']}\n"
        f"- Report date: {data['report_date']}\n"
        f"- Complainant: {data['complainant_name']}\n"
        f"- Respondent: {data['respondent_name']}\n"
        f"- Allegation summary: {data['allegation_summary']}\n"
        f"- Investigation start date: {data['investigation_start_date']}\n"
        f"- Witnesses interviewed: {data.get('witnesses') or 'None'}\n"
        f"- Evidence reviewed: {data.get('evidence_reviewed') or 'None'}\n"
        f"- Findings: {data['findings']}\n"
        f"- Outcome: {data['outcome']}\n"
        f"- Recommendations: {data.get('recommendations') or 'None'}\n\n"
        f"Write a formal workplace investigation report following best practice for {country_name}. "
        f"Structure it with clear sections: Executive Summary, Background, Investigation Process, "
        f"Findings, Conclusion, and Recommendations. Maintain an objective, professional tone. "
        f"Output the report text only — no preamble or explanation."
    )


@router.get("/", response_class=HTMLResponse)
async def documents_hub(request: Request, user: User = Depends(get_current_user)):
    if not user.is_subscribed:
        return RedirectResponse("/subscribe", status_code=303)
    return templates.TemplateResponse(
        request,
        "documents.html",
        {"user": user, "document_types": DOCUMENT_TYPES},
    )


@router.get("/{doc_type}", response_class=HTMLResponse)
async def document_form(
    doc_type: str,
    request: Request,
    user: User = Depends(get_current_user),
):
    if not user.is_subscribed:
        return RedirectResponse("/subscribe", status_code=303)
    if doc_type not in DOCUMENT_TYPES:
        return RedirectResponse("/documents", status_code=303)
    return templates.TemplateResponse(
        request,
        "document_form.html",
        {
            "user": user,
            "doc_type": doc_type,
            "doc_info": DOCUMENT_TYPES[doc_type],
            "countries": COUNTRY_NAMES,
        },
    )


@router.post("/{doc_type}/generate", response_class=HTMLResponse)
async def generate_document(
    doc_type: str,
    request: Request,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    if not user.is_subscribed:
        return RedirectResponse("/subscribe", status_code=303)
    if doc_type not in DOCUMENT_TYPES:
        return RedirectResponse("/documents", status_code=303)

    form = await request.form()
    country = str(form.get("country", "us"))
    data = {k: str(v).strip() for k, v in form.items()}

    if doc_type == "resignation":
        prompt = _build_resignation_prompt(country, data)
    elif doc_type == "warning":
        prompt = _build_warning_prompt(country, data)
    elif doc_type == "termination":
        prompt = _build_termination_prompt(country, data)
    else:
        prompt = _build_investigation_prompt(country, data)

    try:
        client = _get_client()
        response = await client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        await record_spend(db, MODEL, response.usage)
        document_text = response.content[0].text
    except Exception as exc:
        return templates.TemplateResponse(
            request,
            "document_form.html",
            {
                "user": user,
                "doc_type": doc_type,
                "doc_info": DOCUMENT_TYPES[doc_type],
                "countries": COUNTRY_NAMES,
                "error": f"AI service error: {exc}",
            },
            status_code=502,
        )

    country_name = COUNTRY_NAMES.get(country, "United States")
    return templates.TemplateResponse(
        request,
        "document_result.html",
        {
            "user": user,
            "doc_type": doc_type,
            "doc_info": DOCUMENT_TYPES[doc_type],
            "document_text": document_text,
            "country_name": country_name,
        },
    )

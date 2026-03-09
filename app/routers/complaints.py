"""Complaint filing routes — step-by-step guided flow."""

import html as html_mod

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..email import is_smtp_configured, send_complaint_email
from ..models.complaint import Complaint
from ..models.user import User
from .authorities_data import get_authority
from .policies import COUNTRY_NAMES

router = APIRouter(prefix="/complaints")
templates = Jinja2Templates(directory="app/templates")

COMPLAINT_CATEGORIES = [
    ("discrimination", "Discrimination"),
    ("retaliation", "Retaliation / Whistleblower"),
    ("wage_theft", "Wage Theft / Unpaid Wages"),
    ("harassment", "Harassment"),
    ("safety", "Unsafe Working Conditions"),
    ("leave", "Leave / Accommodation Denial"),
    ("other", "Other"),
]

_CATEGORY_LABELS = dict(COMPLAINT_CATEGORIES)


def _build_complaint_email_body(user: User, complaint: Complaint, category_label: str) -> str:
    """Build an HTML email body for a complaint submission."""
    esc = html_mod.escape
    return f"""\
<html><body>
<h2>Workplace Complaint Submission</h2>
<p><strong>From:</strong> {esc(user.full_name)} ({esc(user.email)})</p>
<p><strong>Category:</strong> {esc(category_label)}</p>
<p><strong>Employer:</strong> {esc(complaint.employer_name or "Not specified")}</p>
<p><strong>Incident Date:</strong> {esc(complaint.incident_date or "Not specified")}</p>
<h3>Description</h3>
<p>{esc(complaint.description)}</p>
{f"<h3>Desired Outcome</h3><p>{esc(complaint.desired_outcome)}</p>" if complaint.desired_outcome else ""}
{f"<h3>Supporting Details</h3><p>{esc(complaint.supporting_details)}</p>" if complaint.supporting_details else ""}
</body></html>"""


@router.get("/", response_class=HTMLResponse)
async def complaints_list(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Complaint).where(Complaint.user_id == user.id).order_by(Complaint.updated_at.desc())
    )
    complaints = result.scalars().all()
    return templates.TemplateResponse(
        "complaints.html", {"request": request, "user": user, "complaints": complaints}
    )


@router.get("/new", response_class=HTMLResponse)
async def new_complaint(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        "complaint_form.html",
        {"request": request, "user": user, "categories": COMPLAINT_CATEGORIES, "complaint": None},
    )


@router.post("/new")
async def create_complaint(
    request: Request,
    category: str = Form(...),
    description: str = Form(...),
    employer_name: str = Form(""),
    incident_date: str = Form(""),
    desired_outcome: str = Form(""),
    supporting_details: str = Form(""),
    action: str = Form("save"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    complaint = Complaint(
        user_id=user.id,
        category=category,
        description=description,
        employer_name=employer_name,
        incident_date=incident_date,
        desired_outcome=desired_outcome,
        supporting_details=supporting_details,
        status="draft",
    )
    db.add(complaint)
    await db.commit()
    await db.refresh(complaint)

    if action == "review":
        return RedirectResponse(f"/complaints/{complaint.id}/preview", status_code=303)
    return RedirectResponse("/complaints", status_code=303)


@router.get("/{complaint_id}", response_class=HTMLResponse)
async def view_complaint(
    complaint_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Complaint).where(Complaint.id == complaint_id, Complaint.user_id == user.id)
    )
    complaint = result.scalar_one_or_none()
    if not complaint:
        return RedirectResponse("/complaints", status_code=303)
    return templates.TemplateResponse(
        "complaint_detail.html",
        {
            "request": request,
            "user": user,
            "complaint": complaint,
            "categories": COMPLAINT_CATEGORIES,
        },
    )


@router.get("/{complaint_id}/preview", response_class=HTMLResponse)
async def preview_complaint(
    complaint_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Complaint).where(Complaint.id == complaint_id, Complaint.user_id == user.id)
    )
    complaint = result.scalar_one_or_none()
    if not complaint or complaint.status != "draft":
        return RedirectResponse("/complaints", status_code=303)

    authority = get_authority(user.country, complaint.category)
    category_label = _CATEGORY_LABELS.get(complaint.category, complaint.category)
    country_name = COUNTRY_NAMES.get(user.country, user.country)
    smtp_ok = is_smtp_configured()

    return templates.TemplateResponse(
        "complaint_preview.html",
        {
            "request": request,
            "user": user,
            "complaint": complaint,
            "authority": authority,
            "category_label": category_label,
            "country_name": country_name,
            "smtp_configured": smtp_ok,
            "categories": COMPLAINT_CATEGORIES,
        },
    )


@router.post("/{complaint_id}/submit")
async def submit_complaint(
    complaint_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Complaint).where(Complaint.id == complaint_id, Complaint.user_id == user.id)
    )
    complaint = result.scalar_one_or_none()
    if not complaint or complaint.status != "draft":
        return RedirectResponse("/complaints", status_code=303)

    authority = get_authority(user.country, complaint.category)
    category_label = _CATEGORY_LABELS.get(complaint.category, complaint.category)

    complaint.authority_name = authority.name
    complaint.authority_email = authority.email
    complaint.authority_portal_url = authority.portal_url
    complaint.status = "submitted"

    if authority.email:
        body = _build_complaint_email_body(user, complaint, category_label)
        subject = f"Workplace Complaint: {category_label}"
        sent = await send_complaint_email(
            to_email=authority.email,
            subject=subject,
            html_body=body,
            reply_to=user.email,
        )
        complaint.email_sent = sent

    await db.commit()
    return RedirectResponse(f"/complaints/{complaint.id}", status_code=303)


@router.get("/{complaint_id}/edit", response_class=HTMLResponse)
async def edit_complaint(
    complaint_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Complaint).where(Complaint.id == complaint_id, Complaint.user_id == user.id)
    )
    complaint = result.scalar_one_or_none()
    if not complaint or complaint.status not in ("draft",):
        return RedirectResponse("/complaints", status_code=303)
    return templates.TemplateResponse(
        "complaint_form.html",
        {
            "request": request,
            "user": user,
            "complaint": complaint,
            "categories": COMPLAINT_CATEGORIES,
        },
    )


@router.post("/{complaint_id}/edit")
async def update_complaint(
    complaint_id: int,
    request: Request,
    category: str = Form(...),
    description: str = Form(...),
    employer_name: str = Form(""),
    incident_date: str = Form(""),
    desired_outcome: str = Form(""),
    supporting_details: str = Form(""),
    action: str = Form("save"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Complaint).where(Complaint.id == complaint_id, Complaint.user_id == user.id)
    )
    complaint = result.scalar_one_or_none()
    if not complaint or complaint.status != "draft":
        return RedirectResponse("/complaints", status_code=303)

    complaint.category = category
    complaint.description = description
    complaint.employer_name = employer_name
    complaint.incident_date = incident_date
    complaint.desired_outcome = desired_outcome
    complaint.supporting_details = supporting_details

    await db.commit()

    if action == "review":
        return RedirectResponse(f"/complaints/{complaint.id}/preview", status_code=303)
    return RedirectResponse("/complaints", status_code=303)

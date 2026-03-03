"""Complaint filing routes — step-by-step guided flow."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models.complaint import Complaint
from ..models.user import User

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
    status = "submitted" if action == "submit" else "draft"
    complaint = Complaint(
        user_id=user.id,
        category=category,
        description=description,
        employer_name=employer_name,
        incident_date=incident_date,
        desired_outcome=desired_outcome,
        supporting_details=supporting_details,
        status=status,
    )
    db.add(complaint)
    await db.commit()
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
    if action == "submit":
        complaint.status = "submitted"

    await db.commit()
    return RedirectResponse("/complaints", status_code=303)

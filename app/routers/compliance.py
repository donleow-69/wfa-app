"""Employer compliance tracking routes."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models.compliance import ComplianceChecklist, ComplianceItem
from ..models.user import User

router = APIRouter(prefix="/compliance")
templates = Jinja2Templates(directory="app/templates")

# Default checklist items seeded for new checklists.
DEFAULT_ITEMS = [
    {
        "category": "Policies",
        "requirement": "Anti-discrimination policy posted and distributed",
        "description": "Written policy covering all protected classes, distributed to all employees and posted in common areas.",
    },
    {
        "category": "Policies",
        "requirement": "Anti-retaliation policy in place",
        "description": "Clear policy prohibiting retaliation against employees who report violations or participate in investigations.",
    },
    {
        "category": "Policies",
        "requirement": "Complaint and reporting procedures documented",
        "description": "Accessible procedure for employees to report concerns, including multiple reporting channels.",
    },
    {
        "category": "Wages",
        "requirement": "Wage and hour compliance audit",
        "description": "Review of pay practices, overtime calculations, and classification of exempt vs. non-exempt employees.",
    },
    {
        "category": "Wages",
        "requirement": "Pay equity analysis completed",
        "description": "Analysis of compensation across roles to identify and address unjustified pay disparities.",
    },
    {
        "category": "Safety",
        "requirement": "OSHA compliance review",
        "description": "Workplace hazard assessment, safety training records, and injury log (OSHA 300) up to date.",
    },
    {
        "category": "Safety",
        "requirement": "Emergency action plan current",
        "description": "Written emergency plan covering evacuation, reporting, and employee notification procedures.",
    },
    {
        "category": "Training",
        "requirement": "Harassment prevention training conducted",
        "description": "Annual training for all employees; supervisors receive additional training on responsibilities.",
    },
    {
        "category": "Training",
        "requirement": "Manager training on accommodation requests",
        "description": "Managers trained on handling disability and religious accommodation requests through interactive process.",
    },
    {
        "category": "Records",
        "requirement": "Employee records retention policy",
        "description": "Personnel files, payroll records, and I-9 forms retained per federal and state requirements.",
    },
    {
        "category": "Leave",
        "requirement": "FMLA eligibility notices posted",
        "description": "Required FMLA poster displayed; eligible employees notified of rights within 5 business days of leave request.",
    },
]


@router.get("/", response_class=HTMLResponse)
async def compliance_dashboard(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ComplianceChecklist).where(ComplianceChecklist.user_id == user.id)
    )
    checklists = result.scalars().all()
    return templates.TemplateResponse(
        "compliance.html", {"request": request, "user": user, "checklists": checklists}
    )


@router.post("/create")
async def create_checklist(
    request: Request,
    company_name: str = Form(""),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    checklist = ComplianceChecklist(user_id=user.id, company_name=company_name)
    db.add(checklist)
    await db.flush()

    for item_data in DEFAULT_ITEMS:
        item = ComplianceItem(
            checklist_id=checklist.id,
            requirement=item_data["requirement"],
            description=item_data["description"],
            category=item_data["category"],
        )
        db.add(item)

    await db.commit()
    return RedirectResponse(f"/compliance/{checklist.id}", status_code=303)


@router.get("/{checklist_id}", response_class=HTMLResponse)
async def view_checklist(
    checklist_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ComplianceChecklist).where(
            ComplianceChecklist.id == checklist_id, ComplianceChecklist.user_id == user.id
        )
    )
    checklist = result.scalar_one_or_none()
    if not checklist:
        return RedirectResponse("/compliance", status_code=303)

    items_result = await db.execute(
        select(ComplianceItem).where(ComplianceItem.checklist_id == checklist_id)
    )
    items = items_result.scalars().all()

    categories = {}
    for item in items:
        categories.setdefault(item.category, []).append(item)

    completed = sum(1 for i in items if i.completed)
    total = len(items)

    return templates.TemplateResponse(
        "checklist.html",
        {
            "request": request,
            "user": user,
            "checklist": checklist,
            "categories": categories,
            "completed": completed,
            "total": total,
        },
    )


@router.post("/{checklist_id}/toggle/{item_id}")
async def toggle_item(
    checklist_id: int,
    item_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ComplianceItem)
        .join(ComplianceChecklist)
        .where(
            ComplianceItem.id == item_id,
            ComplianceChecklist.id == checklist_id,
            ComplianceChecklist.user_id == user.id,
        )
    )
    item = result.scalar_one_or_none()
    if item:
        item.completed = not item.completed
        await db.commit()
    return RedirectResponse(f"/compliance/{checklist_id}", status_code=303)

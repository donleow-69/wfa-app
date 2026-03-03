"""Employee rights information pages."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..auth import get_optional_user
from ..models.user import User

router = APIRouter(prefix="/rights")
templates = Jinja2Templates(directory="app/templates")

# Structured WFA rights data — easy to update as legislation evolves.
RIGHTS_CATEGORIES = [
    {
        "id": "discrimination",
        "title": "Anti-Discrimination Protections",
        "icon": "shield",
        "summary": "Protection against workplace discrimination based on protected characteristics.",
        "details": [
            "Employers cannot discriminate based on race, color, religion, sex, national origin, age, disability, or genetic information.",
            "Equal pay for substantially similar work regardless of gender.",
            "Reasonable accommodations must be provided for disabilities and religious practices.",
            "Hiring, firing, promotion, and compensation decisions must be based on merit.",
        ],
        "what_to_do": "Document specific instances with dates, witnesses, and any written communications. File a complaint through this app or contact the EEOC.",
    },
    {
        "id": "retaliation",
        "title": "Whistleblower & Retaliation Protections",
        "icon": "megaphone",
        "summary": "You cannot be punished for reporting violations or exercising your rights.",
        "details": [
            "Employers cannot retaliate against employees who report workplace violations.",
            "Protection covers filing complaints, participating in investigations, or refusing illegal orders.",
            "Retaliation includes termination, demotion, pay cuts, schedule changes, or hostile treatment.",
            "Protections apply even if the original complaint is not ultimately upheld.",
        ],
        "what_to_do": "Keep a timeline of events showing the connection between your protected activity and the adverse action. Save all communications.",
    },
    {
        "id": "wages",
        "title": "Wage & Hour Rights",
        "icon": "banknotes",
        "summary": "Your right to fair compensation for all hours worked.",
        "details": [
            "Minimum wage and overtime protections for eligible workers.",
            "Employers must pay for all hours worked, including required training and travel time.",
            "Pay stubs must be provided with detailed breakdowns.",
            "Final paychecks must be issued within the timeframe required by state law.",
        ],
        "what_to_do": "Keep your own records of hours worked. Compare pay stubs against actual hours. Report discrepancies promptly.",
    },
    {
        "id": "safety",
        "title": "Workplace Safety",
        "icon": "hard-hat",
        "summary": "Your right to a safe and healthy work environment.",
        "details": [
            "Employers must provide a workplace free from recognized hazards.",
            "You have the right to request an OSHA inspection without retaliation.",
            "Access to training, safety equipment, and injury/illness records.",
            "Right to refuse work that poses imminent danger to life or health.",
        ],
        "what_to_do": "Report hazards to your supervisor in writing. If unresolved, file a complaint with OSHA. Document unsafe conditions with photos and dates.",
    },
    {
        "id": "leave",
        "title": "Leave & Accommodations",
        "icon": "calendar",
        "summary": "Your right to medical leave, family leave, and reasonable accommodations.",
        "details": [
            "FMLA provides up to 12 weeks of unpaid, job-protected leave for qualifying reasons.",
            "Employers must engage in an interactive process for disability accommodations.",
            "Pregnancy-related accommodations must be provided.",
            "You cannot be penalized for using legally protected leave.",
        ],
        "what_to_do": "Request accommodations or leave in writing. Keep copies of medical documentation you submit. Note your employer's response and timeline.",
    },
]


@router.get("/", response_class=HTMLResponse)
async def rights_overview(request: Request, user: User | None = Depends(get_optional_user)):
    return templates.TemplateResponse(
        "rights.html",
        {"request": request, "user": user, "categories": RIGHTS_CATEGORIES},
    )


@router.get("/{category_id}", response_class=HTMLResponse)
async def rights_detail(
    category_id: str, request: Request, user: User | None = Depends(get_optional_user)
):
    category = next((c for c in RIGHTS_CATEGORIES if c["id"] == category_id), None)
    if not category:
        return templates.TemplateResponse(
            "404.html", {"request": request, "user": user}, status_code=404
        )
    return templates.TemplateResponse(
        "rights_detail.html",
        {"request": request, "user": user, "category": category},
    )

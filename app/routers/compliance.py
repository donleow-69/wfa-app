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

# Default checklist items seeded for new checklists, by country.
DEFAULT_ITEMS_BY_COUNTRY = {
    "us": [
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
    ],
    "sg": [
        {
            "category": "Policies",
            "requirement": "Workplace Fairness Act-compliant fair employment policy adopted",
            "description": "Written policy compliant with the Workplace Fairness Act covering merit-based hiring, non-discrimination, and fair HR practices.",
        },
        {
            "category": "Policies",
            "requirement": "Anti-harassment policy in place (POHA-aligned)",
            "description": "Policy addressing workplace harassment and bullying, aligned with the Protection from Harassment Act.",
        },
        {
            "category": "Policies",
            "requirement": "Data protection policy compliant with PDPA",
            "description": "Employee data protection policy compliant with the Personal Data Protection Act 2012, including DPO appointment and consent procedures.",
        },
        {
            "category": "Employment",
            "requirement": "Key Employment Terms issued to all employees",
            "description": "Written KET provided within 14 days of employment start, covering job scope, salary, working hours, leave, and notice period per Employment Act (Cap. 91).",
        },
        {
            "category": "Employment",
            "requirement": "Itemised payslips provided",
            "description": "Itemised payslips issued for each salary payment showing basic salary, allowances, deductions, overtime, and net pay per Employment Act requirements.",
        },
        {
            "category": "Wages",
            "requirement": "CPF contributions up to date",
            "description": "Central Provident Fund contributions calculated and remitted correctly for all eligible employees at current rates.",
        },
        {
            "category": "Wages",
            "requirement": "Overtime and working hours compliance",
            "description": "Working hours within 44 hrs/week limit, overtime capped at 72 hrs/month, overtime pay at 1.5x rate for Part IV employees.",
        },
        {
            "category": "Safety",
            "requirement": "WSHA risk assessment completed",
            "description": "Risk assessments conducted for all work activities per Workplace Safety and Health Act. Control measures implemented and reviewed regularly.",
        },
        {
            "category": "Safety",
            "requirement": "Incident reporting procedures in place",
            "description": "Procedures for reporting workplace accidents, dangerous occurrences, and occupational diseases to MOM as required under WSHA.",
        },
        {
            "category": "Foreign Workers",
            "requirement": "Work pass validity and conditions reviewed",
            "description": "All foreign employees hold valid work passes. No passport retention, no salary kickbacks, acceptable accommodation and medical coverage per EFMA.",
        },
        {
            "category": "Foreign Workers",
            "requirement": "Compulsory insurance for foreign workers",
            "description": "Medical insurance (min $15,000/year inpatient) for all Work Permit and S Pass holders. Personal accident insurance (min $40,000) for Work Permit holders. Policies must remain valid throughout employment.",
        },
        {
            "category": "Leave",
            "requirement": "Statutory leave entitlements communicated",
            "description": "Employees informed of annual leave (7-14 days), sick leave (14 days outpatient, 60 days hospitalisation), maternity (16 weeks), paternity (2 weeks), and childcare leave entitlements.",
        },
    ],
    "my": [
        {
            "category": "Policies",
            "requirement": "Sexual harassment policy displayed (EA s81H)",
            "description": "Conspicuous notice on sexual harassment posted at workplace and inquiry procedures established per Section 81H of Employment Act 1955.",
        },
        {
            "category": "Policies",
            "requirement": "Anti-discrimination and fair employment policy adopted",
            "description": "Written policy on equal opportunity covering fair hiring and non-discrimination aligned with Industrial Relations Act 1967.",
        },
        {
            "category": "Policies",
            "requirement": "Complaint and grievance procedures documented",
            "description": "Accessible procedure for employees to report concerns including discrimination, harassment, and unfair treatment.",
        },
        {
            "category": "Employment",
            "requirement": "Employment contracts compliant with EA 1955",
            "description": "Written employment contracts issued covering working hours (45 hrs/week max), overtime rates, leave entitlements, and notice periods per EA 1955 as amended.",
        },
        {
            "category": "Employment",
            "requirement": "Flexible working arrangement process in place",
            "description": "Process for employees to apply for flexible working arrangements (hours, days, location) with written response within 60 days per 2022 amendment.",
        },
        {
            "category": "Wages",
            "requirement": "Minimum wage and overtime compliance",
            "description": "All employees paid at least applicable minimum wage. Overtime at 1.5x (normal day), 2x (rest day), 3x (public holiday). Wages paid within 7 days of salary period end.",
        },
        {
            "category": "Wages",
            "requirement": "EPF and SOCSO contributions current",
            "description": "Employees' Provident Fund (EPF) and Social Security Organisation (SOCSO/PERKESO) contributions calculated and remitted on time.",
        },
        {
            "category": "Safety",
            "requirement": "OSHA 1994 compliance review",
            "description": "Workplace safety assessment per Occupational Safety and Health Act 1994. Safety and Health Committee established, risk assessments completed, DOSH reporting procedures in place.",
        },
        {
            "category": "Leave",
            "requirement": "Statutory leave entitlements verified",
            "description": "Annual leave (8-16 days), sick leave (14-22 days), hospitalisation (60 days), maternity (98 days), paternity (7 days), and public holidays (11 days) provided per EA 1955.",
        },
        {
            "category": "Foreign Workers",
            "requirement": "Foreign worker compliance audit",
            "description": "Valid work permits for all foreign workers, no passport retention (Passport Act 1966), SOCSO/medical coverage provided, anti-trafficking obligations met (ATIPSOM 2007).",
        },
        {
            "category": "Training",
            "requirement": "Harassment prevention training conducted",
            "description": "Training on sexual harassment awareness and reporting procedures for all employees, with additional training for managers.",
        },
    ],
    "id": [
        {
            "category": "Employment",
            "requirement": "Employment contracts compliant with Manpower Act",
            "description": "Written contracts (PKWT/PKWTT) issued per Law No. 13/2003 and Omnibus Law. Fixed-term contracts within maximum duration limits.",
        },
        {
            "category": "Employment",
            "requirement": "Working hours and overtime compliance",
            "description": "Working hours within 40 hrs/week, overtime limited to 4 hrs/day and 18 hrs/week, overtime paid at 1.5x (first hour) and 2x (subsequent) per Manpower Act.",
        },
        {
            "category": "Wages",
            "requirement": "Minimum wage compliance verified",
            "description": "All employees paid at least the applicable provincial/district minimum wage. Wages paid in Rupiah on regular schedule.",
        },
        {
            "category": "Policies",
            "requirement": "Non-discrimination policy adopted (Articles 5-6)",
            "description": "Written equal opportunity policy implementing Manpower Act Articles 5 and 6 — no discrimination based on gender, ethnicity, race, religion, or political views.",
        },
        {
            "category": "Policies",
            "requirement": "Women's protections communicated",
            "description": "Female employees informed of maternity leave (3 months), menstrual leave, breastfeeding rights, and night work protections per Manpower Act.",
        },
        {
            "category": "Social Security",
            "requirement": "BPJS Ketenagakerjaan enrollment and contributions current",
            "description": "All employees enrolled in JKK, JKM, JHT, and JP programmes. Employer and employee contributions calculated correctly and remitted by the 15th of each month per Law No. 24/2011.",
        },
        {
            "category": "Social Security",
            "requirement": "BPJS Kesehatan enrollment and contributions current",
            "description": "All employees and eligible family members enrolled in BPJS Kesehatan. Contributions (5% of wages) remitted on time per Law No. 40/2004.",
        },
        {
            "category": "Safety",
            "requirement": "Workplace safety compliance (Law No. 1/1970)",
            "description": "Workplace inspections and risk assessments completed. Safety training and PPE provided. SMK3 system maintained where required.",
        },
        {
            "category": "Leave",
            "requirement": "Statutory leave entitlements provided",
            "description": "Annual leave (12 days after 12 months), maternity (3 months full pay), menstrual leave, sick leave, and bereavement leave provided per Manpower Act.",
        },
        {
            "category": "Termination",
            "requirement": "Termination and severance procedures documented",
            "description": "Termination only for valid legal grounds. Severance pay, service appreciation pay, and compensation for entitlements calculated per Omnibus Law. Bipartite negotiation procedures in place.",
        },
    ],
    "ph": [
        {
            "category": "Employment",
            "requirement": "Labor Code compliance on working hours and overtime",
            "description": "Normal hours at 8/day, overtime at +25% (ordinary) / +30% (rest/holiday), night shift differential at +10% for 10PM-6AM work.",
        },
        {
            "category": "Employment",
            "requirement": "Security of tenure and due process procedures documented",
            "description": "Twin-notice rule procedures in place for just cause terminations (Art 297). Authorised cause procedures (Art 298-299) with 30-day notice to employee and DOLE.",
        },
        {
            "category": "Wages",
            "requirement": "Regional minimum wage compliance",
            "description": "All employees paid at least the applicable regional daily minimum wage per RA 6727. Wage adjustments implemented within prescribed period.",
        },
        {
            "category": "Wages",
            "requirement": "13th month pay compliance (PD 851)",
            "description": "All rank-and-file employees receive 13th month pay (1/12 of total basic salary) no later than December 24.",
        },
        {
            "category": "Wages",
            "requirement": "SSS, PhilHealth, and Pag-IBIG contributions current",
            "description": "Employer and employee shares remitted on time for Social Security System, Philippine Health Insurance, and Home Development Mutual Fund.",
        },
        {
            "category": "Policies",
            "requirement": "Anti-sexual harassment policy and CODI established",
            "description": "Policy compliant with RA 7877 and RA 11313 (Safe Spaces Act). Committee on Decorum and Investigation (CODI) established with management, employee, and union representatives.",
        },
        {
            "category": "Policies",
            "requirement": "Complaint and grievance mechanism in place",
            "description": "Accessible procedure for employees to report harassment, discrimination, and other workplace concerns with multiple reporting channels.",
        },
        {
            "category": "Safety",
            "requirement": "OSH Standards Act compliance (RA 11058)",
            "description": "Safety Officer designated, Safety Committee established, OSH training provided, PPE furnished at no cost, and incident reports filed with DOLE.",
        },
        {
            "category": "Leave",
            "requirement": "Statutory leave entitlements provided",
            "description": "Service incentive leave (5 days), maternity (105 days per RA 11210), paternity (7 days per RA 8187), solo parent leave (7 days per RA 8972), special leave for women (2 months per RA 9710).",
        },
        {
            "category": "Training",
            "requirement": "Gender sensitivity and harassment prevention training",
            "description": "Training on RA 7877 and Safe Spaces Act conducted for all employees. CODI members trained on investigation procedures.",
        },
        {
            "category": "Records",
            "requirement": "Employment records maintained per DOLE requirements",
            "description": "Payroll records, daily time records, and employee 201 files maintained for at least 3 years as required by the Labor Code.",
        },
    ],
    "th": [
        {
            "category": "Employment",
            "requirement": "Labor Protection Act compliance on hours and wages",
            "description": "Working hours within 8 hrs/day and 48 hrs/week (42 for hazardous work). Minimum wage paid. Overtime at 1.5x (working day), 3x (holiday overtime).",
        },
        {
            "category": "Employment",
            "requirement": "Work Rules registered (20+ employees)",
            "description": "Written Work Rules in Thai posted at the workplace and a copy filed with the Labour Inspector within 15 days, as required for employers with 20 or more employees.",
        },
        {
            "category": "Employment",
            "requirement": "Severance pay schedule documented",
            "description": "Severance pay rates communicated: 30 days (120d-3yr), 90 days (3-6yr), 200 days (6-10yr), 300 days (10-20yr), 400 days (20+yr) per LPA.",
        },
        {
            "category": "Wages",
            "requirement": "Social Security contributions current",
            "description": "Employer (5%) and employee (5%) contributions calculated on wages up to THB 15,000 ceiling and remitted to SSO by the 15th of the following month per Social Security Act B.E. 2533.",
        },
        {
            "category": "Wages",
            "requirement": "Provident Fund compliance (if applicable)",
            "description": "If a provident fund is established, contributions remitted per the Provident Fund Act. Employee informed of fund terms and entitlements.",
        },
        {
            "category": "Policies",
            "requirement": "Anti-harassment measures in place (LPA s16)",
            "description": "Policy addressing sexual harassment by employers/supervisors per LPA Section 16 and gender-based discrimination per Gender Equality Act B.E. 2558.",
        },
        {
            "category": "Policies",
            "requirement": "Complaint mechanism established",
            "description": "Accessible channels for employees to report harassment, discrimination, and workplace concerns. Option to file with the Committee on Consideration of Unfair Gender Discrimination.",
        },
        {
            "category": "Safety",
            "requirement": "OSH Act B.E. 2554 compliance",
            "description": "Safety Officer appointed, Safety Committee established (50+ employees), risk assessments completed, OSH training provided, and accidents reported per prescribed timeframes.",
        },
        {
            "category": "Leave",
            "requirement": "Statutory leave entitlements provided",
            "description": "Annual leave (6+ days), sick leave (30 days paid), maternity (98 days), personal business leave (3 days), and 13+ public holidays per LPA.",
        },
        {
            "category": "Training",
            "requirement": "Harassment prevention and gender equality training",
            "description": "Employees trained on anti-harassment obligations under LPA Section 16 and Gender Equality Act. Supervisors trained on complaint handling.",
        },
    ],
    "gb": [
        {
            "category": "Immigration",
            "requirement": "Right to work checks completed",
            "description": "Conduct right-to-work checks for all new employees before start date; maintain records and track visa expiry dates. Penalty: up to GBP 60,000 per illegal worker.",
        },
        {
            "category": "Pensions",
            "requirement": "Auto-enrolment pension scheme active",
            "description": "Enrol eligible workers (aged 22+, earning over GBP 10,000/year) into a qualifying pension scheme. Minimum contributions: 3% employer, 5% employee.",
        },
        {
            "category": "Wages",
            "requirement": "National Minimum/Living Wage compliance",
            "description": "Pay at least GBP 12.71/hour for workers aged 21+ (from April 2026). Maintain detailed payroll records.",
        },
        {
            "category": "Contracts",
            "requirement": "Written employment particulars issued",
            "description": "Provide written statement of employment particulars on or before day one of employment as required by the Employment Rights Act 1996.",
        },
        {
            "category": "Safety",
            "requirement": "Health and safety risk assessments documented",
            "description": "Conduct and document risk assessments under HSWA 1974. Written health and safety policy mandatory if 5 or more employees.",
        },
        {
            "category": "Equality",
            "requirement": "Anti-harassment and equal opportunities policies",
            "description": "Implement policies covering all nine protected characteristics under the Equality Act 2010. Take all reasonable steps to prevent sexual harassment (ERA 2025 duty).",
        },
        {
            "category": "Working Time",
            "requirement": "Working time compliance verified",
            "description": "Ensure 48-hour week cap (or signed opt-outs), daily and weekly rest breaks, and minimum 28 days annual leave including bank holidays.",
        },
        {
            "category": "Whistleblowing",
            "requirement": "Whistleblowing policy established",
            "description": "Establish a whistleblowing policy with clear reporting channels and protections for workers making protected disclosures under PIDA 1998.",
        },
        {
            "category": "Tax",
            "requirement": "Employer NIC registered",
            "description": "Register for employer National Insurance Contributions at 15% rate. Apply Employment Allowance (GBP 10,500) if eligible.",
        },
        {
            "category": "ERA 2025",
            "requirement": "ERA 2025 readiness reviewed",
            "description": "Review probation/dismissal procedures for 6-month qualifying period (January 2027), trade union access agreements (April 2026), and SSP day-one entitlement.",
        },
    ],
    "hk": [
        {
            "category": "Contracts",
            "requirement": "Written employment contracts executed",
            "description": "Execute written employment contracts covering mandatory terms: wages, hours, rest days, notice period, and end-of-year payment before or at commencement.",
        },
        {
            "category": "Wages",
            "requirement": "Statutory Minimum Wage compliance",
            "description": "Pay at least HKD 43.1/hour (from May 2026). Maintain detailed wage and time records for at least 12 months.",
        },
        {
            "category": "MPF",
            "requirement": "MPF scheme enrolment",
            "description": "Enrol all eligible employees in an MPF scheme within 60 days of employment start. Contribute 5% of relevant income (capped at HKD 1,500/month).",
        },
        {
            "category": "Immigration",
            "requirement": "Work visa verification",
            "description": "Verify immigration and work visa status of all non-permanent residents before employment. Maintain records. Penalty: HKD 350,000 fine and 3 years imprisonment.",
        },
        {
            "category": "Leave",
            "requirement": "Statutory leave entitlements provided",
            "description": "Provide rest days, 15 statutory holidays (2026), annual leave (7-14 days based on service), sick leave, maternity (14 weeks), and paternity (5 days) leave.",
        },
        {
            "category": "Continuous Contract",
            "requirement": "Broadened continuous contract compliance",
            "description": "Under Employment (Amendment) Ordinance 2025 (effective January 2026), employees working 68+ hours over 4 consecutive weeks qualify for full statutory protections.",
        },
        {
            "category": "Equality",
            "requirement": "Anti-discrimination and anti-harassment policies",
            "description": "Implement policies covering sex, disability, family status, and race discrimination under the four discrimination ordinances. Train managers on obligations.",
        },
        {
            "category": "Safety",
            "requirement": "Workplace risk assessments completed",
            "description": "Comply with the Occupational Safety and Health Ordinance (Cap 509). Report workplace accidents to the Labour Department within specified timeframes.",
        },
        {
            "category": "MPF Offsetting",
            "requirement": "MPF offsetting abolition compliance",
            "description": "Since May 2025, employer mandatory MPF contributions cannot offset severance pay or long service payments for post-transition service. Budget separately.",
        },
        {
            "category": "Working Hours",
            "requirement": "Duty of care for working hours",
            "description": "No statutory maximum working hours in Hong Kong, but employers owe a common law duty of care regarding overwork and employee wellbeing.",
        },
    ],
}

# Backwards-compatible alias.
DEFAULT_ITEMS = DEFAULT_ITEMS_BY_COUNTRY["us"]


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

    items = DEFAULT_ITEMS_BY_COUNTRY.get(user.country, DEFAULT_ITEMS_BY_COUNTRY["us"])
    for item_data in items:
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

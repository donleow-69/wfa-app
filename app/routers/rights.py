"""Employee rights information pages."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..auth import get_optional_user
from ..models.user import User

router = APIRouter(prefix="/rights")
templates = Jinja2Templates(directory="app/templates")

COUNTRY_NAMES = {
    "us": "United States",
    "sg": "Singapore",
    "my": "Malaysia",
    "id": "Indonesia",
    "ph": "Philippines",
    "th": "Thailand",
}

RIGHTS_BY_COUNTRY = {
    "us": [
        {
            "id": "discrimination",
            "title": "Anti-Discrimination Protections",
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
            "summary": "Your right to medical leave, family leave, and reasonable accommodations.",
            "details": [
                "FMLA provides up to 12 weeks of unpaid, job-protected leave for qualifying reasons.",
                "Employers must engage in an interactive process for disability accommodations.",
                "Pregnancy-related accommodations must be provided.",
                "You cannot be penalized for using legally protected leave.",
            ],
            "what_to_do": "Request accommodations or leave in writing. Keep copies of medical documentation you submit. Note your employer's response and timeline.",
        },
    ],
    "sg": [
        {
            "id": "employment_act",
            "title": "Employment Act (Cap. 91)",
            "summary": "Singapore's main employment legislation covering wages, hours, leave, and termination.",
            "details": [
                "Covers all employees under a contract of service except seafarers, domestic workers, and public servants.",
                "Maximum 44 working hours per week (or 88 hours over 2 weeks). Overtime capped at 72 hours per month.",
                "Overtime pay at 1.5x the hourly basic rate for non-workmen earning up to S$2,600/month.",
                "Minimum 7 days annual leave after 3 months, increasing to 14 days after 8 years.",
                "11 paid public holidays per year. Sick leave: 14 days outpatient, 60 days hospitalisation.",
                "Employers must issue itemised payslips and key employment terms within 14 days of employment.",
            ],
            "what_to_do": "Keep copies of your employment contract and payslips. Report disputes to the Ministry of Manpower (MOM) or file a claim at the Employment Claims Tribunal.",
        },
        {
            "id": "wsha",
            "title": "Workplace Safety & Health Act (WSHA)",
            "summary": "Requires employers to ensure a safe workplace and manage risks proactively.",
            "details": [
                "Employers must take reasonably practicable measures to ensure safety and health of workers.",
                "Risk assessments must be conducted for all work activities.",
                "Employees must be provided with adequate safety training and personal protective equipment.",
                "Workers have the right to report unsafe conditions to MOM without retaliation.",
                "Workplace injuries and dangerous occurrences must be reported to MOM.",
            ],
            "what_to_do": "Report hazards to your supervisor or safety officer. If unresolved, file a complaint with MOM's Occupational Safety and Health Division.",
        },
        {
            "id": "tafep",
            "title": "TAFEP Fair Employment Practices",
            "summary": "Guidelines against workplace discrimination enforced by the Tripartite Alliance for Fair & Progressive Employment Practices.",
            "details": [
                "Employers should not discriminate based on age, race, gender, religion, marital status, family responsibilities, or disability.",
                "Job advertisements must not state preference for any particular characteristic unless it is an inherent job requirement.",
                "Selection criteria should be based on skills, experience, and ability to perform the job.",
                "The Tripartite Guidelines on Fair Employment Practices (TGFEP) are enforceable under the Employment Act.",
                "From 2024, workplace fairness legislation strengthens protections against discrimination.",
            ],
            "what_to_do": "Report discriminatory practices to TAFEP (tafep.sg). You can file a complaint online or call the TAFEP hotline at 6838 0969.",
        },
        {
            "id": "poha",
            "title": "Protection from Harassment Act (POHA)",
            "summary": "Protects against harassment, bullying, and stalking in the workplace.",
            "details": [
                "Prohibits threatening, abusive, or insulting behaviour that causes harassment, alarm, or distress.",
                "Covers both physical and online harassment (cyberbullying).",
                "Victims can apply for Protection Orders or Expedited Protection Orders from the courts.",
                "Employers can be held liable for harassment by employees in the course of employment.",
                "Stalking, whether physical or through electronic means, is a criminal offence.",
            ],
            "what_to_do": "Document all incidents with screenshots, dates, and witnesses. Report to HR or management. You can apply for a Protection Order at the Protection from Harassment Court.",
        },
        {
            "id": "retirement",
            "title": "Retirement & Re-employment Act",
            "summary": "Protects older workers from premature retirement and ensures re-employment opportunities.",
            "details": [
                "Minimum retirement age is 63 years (raised progressively to 65 by 2030).",
                "Employers must offer re-employment to eligible employees up to age 68 (rising to 70 by 2030).",
                "Re-employment must be on reasonable terms based on the employee's last drawn salary.",
                "Employers who cannot re-employ must offer an Employment Assistance Payment (EAP).",
                "Employers cannot dismiss employees to avoid re-employment obligations.",
            ],
            "what_to_do": "If you are approaching retirement age, request re-employment terms in writing. Disputes can be brought to MOM for mediation.",
        },
        {
            "id": "efma",
            "title": "Employment of Foreign Manpower Act (EFMA)",
            "summary": "Regulates employment of foreign workers and protects their rights.",
            "details": [
                "Foreign workers must hold a valid work pass (Work Permit, S Pass, or Employment Pass).",
                "Employers must not collect or deduct kickbacks from foreign workers' salaries.",
                "Employers must provide acceptable accommodation and bear medical costs for Work Permit holders.",
                "Foreign workers have the same Employment Act protections as local workers.",
                "Employers cannot hold workers' passports or restrict their movement.",
            ],
            "what_to_do": "Report violations to MOM. Foreign workers can seek help from the Migrant Workers' Centre (MWC) or call MOM's helpline at 6438 5122.",
        },
    ],
    "my": [
        {
            "id": "employment_act_1955",
            "title": "Employment Act 1955",
            "summary": "Malaysia's primary employment legislation governing wages, hours, leave, and termination.",
            "details": [
                "Applies to all employees regardless of salary (expanded coverage from 2023 amendments).",
                "Maximum 45 working hours per week. Overtime at 1.5x for normal days, 2x for rest days, 3x for public holidays.",
                "Minimum 8 days annual leave (increasing with years of service), 14 days paid sick leave, 60 days hospitalisation leave.",
                "Maternity leave of 98 days (increased from 60 days) for female employees.",
                "Paternity leave of 7 days for married male employees.",
                "Flexible working arrangement requests must be considered by employers (2023 amendment).",
                "Protection against sexual harassment in the workplace (Section 81H).",
            ],
            "what_to_do": "File complaints with the Labour Department (Jabatan Tenaga Kerja). For sexual harassment cases, lodge a complaint with the employer first, then the Director General of Labour.",
        },
        {
            "id": "industrial_relations",
            "title": "Industrial Relations Act 1967",
            "summary": "Governs employer-employee relations, trade unions, and dispute resolution.",
            "details": [
                "Employees have the right to join and form trade unions.",
                "Employers cannot interfere with or dismiss employees for union activities.",
                "Disputes can be referred to the Industrial Court for adjudication.",
                "Protection against unfair dismissal — employers must have just cause and follow due process.",
                "Collective bargaining agreements are legally binding.",
            ],
            "what_to_do": "Contact the Department of Industrial Relations to mediate disputes. Unfair dismissal claims should be filed within 60 days of termination.",
        },
        {
            "id": "osha_1994",
            "title": "Occupational Safety & Health Act 1994 (OSHA)",
            "summary": "Ensures workplace safety and health standards for all industries.",
            "details": [
                "Employers must ensure, so far as practicable, the safety, health, and welfare of employees.",
                "Risk assessments must be conducted and safety measures implemented.",
                "Employers with 40+ employees must establish a Safety and Health Committee.",
                "Employees have the right to report unsafe conditions without retaliation.",
                "Workplace accidents and dangerous occurrences must be reported to DOSH.",
            ],
            "what_to_do": "Report hazards to your employer's Safety and Health Committee. If unresolved, contact the Department of Occupational Safety and Health (DOSH).",
        },
    ],
    "id": [
        {
            "id": "omnibus_law",
            "title": "Omnibus Law on Job Creation (Law No. 6/2023)",
            "summary": "Indonesia's comprehensive employment reform covering wages, contracts, and severance.",
            "details": [
                "Minimum wage set by provincial governors based on economic conditions and purchasing power.",
                "Fixed-term employment contracts (PKWT) can be extended but limited to 5 years total.",
                "Severance pay required for termination: up to 9 months' salary depending on tenure.",
                "Outsourcing is permitted for supporting activities with worker protections maintained.",
                "Working hours: maximum 7 hours/day (6-day week) or 8 hours/day (5-day week), with overtime up to 4 hours/day.",
                "Overtime pay at 1.5x for the first hour and 2x for subsequent hours.",
            ],
            "what_to_do": "File disputes with the local Manpower Office (Disnaker). Industrial disputes follow bipartite negotiation, then mediation, and finally the Industrial Relations Court.",
        },
        {
            "id": "manpower_act",
            "title": "Manpower Act (Law No. 13/2003)",
            "summary": "Core labour law covering worker rights, social security, and workplace protections.",
            "details": [
                "Prohibition of child labour (under 15 years) with limited exceptions for light work.",
                "Equal opportunity and treatment without discrimination based on gender, ethnicity, race, religion, or political views.",
                "Female workers entitled to 3 months maternity leave (1.5 months before and after birth).",
                "Workers entitled to annual leave of at least 12 days after 12 months of continuous employment.",
                "Workers have the right to form and join trade unions.",
                "Employers must enrol workers in social security (BPJS Ketenagakerjaan and BPJS Kesehatan).",
            ],
            "what_to_do": "Report violations to the nearest Manpower Office. Workers can also seek assistance from trade unions or legal aid organisations.",
        },
    ],
    "ph": [
        {
            "id": "labor_code",
            "title": "Labor Code of the Philippines",
            "summary": "Comprehensive law governing employment, wages, working conditions, and labour relations.",
            "details": [
                "Normal working hours: 8 hours per day. Overtime pay at 25% premium (30% for holidays/rest days).",
                "Minimum wage set by Regional Tripartite Wages and Productivity Boards.",
                "13th month pay mandatory for all rank-and-file employees.",
                "Security of tenure — employees can only be dismissed for just or authorised causes with due process.",
                "Service incentive leave of 5 days for employees who have worked at least 1 year.",
                "Maternity leave of 105 days (RA 11210). Paternity leave of 7 days.",
                "Night shift differential of at least 10% for work between 10pm and 6am.",
            ],
            "what_to_do": "File complaints with the Department of Labor and Employment (DOLE). For illegal dismissal, file a case with the National Labor Relations Commission (NLRC) within 4 years.",
        },
        {
            "id": "osh_standards",
            "title": "Occupational Safety & Health Standards Act (RA 11058)",
            "summary": "Strengthens workplace safety compliance and worker protections.",
            "details": [
                "Employers must provide a safe and healthy workplace at no cost to workers.",
                "Mandatory safety officers and safety committees for establishments with threshold number of workers.",
                "Workers have the right to refuse unsafe work without threat of retaliation.",
                "Employers must report work accidents, occupational diseases, and dangerous occurrences to DOLE.",
                "Workers must receive free OSH training appropriate to their job.",
                "Penalties for non-compliance include fines and possible closure of establishment.",
            ],
            "what_to_do": "Report workplace hazards to your safety officer or DOLE regional office. You can also call the DOLE hotline 1349.",
        },
    ],
    "th": [
        {
            "id": "labor_protection",
            "title": "Labor Protection Act B.E. 2541 (1998)",
            "summary": "Thailand's primary labour law covering wages, hours, leave, and termination protections.",
            "details": [
                "Normal working hours: maximum 8 hours/day and 48 hours/week. Overtime at 1.5x rate.",
                "Minimum wage set by the National Wage Committee (varies by province).",
                "Annual leave of at least 6 working days after 1 year of service.",
                "Sick leave up to 30 working days per year with pay (medical certificate required after 3 days).",
                "Maternity leave of 98 days (45 days paid by employer, remainder by Social Security).",
                "Severance pay required for termination: 30 days to 400 days of wages depending on tenure.",
                "Employers cannot dismiss employees for exercising legal rights, filing complaints, or union activities.",
            ],
            "what_to_do": "File complaints with the Labour Protection and Welfare Office in your province. Disputes can be escalated to the Labour Court.",
        },
        {
            "id": "labor_relations",
            "title": "Labor Relations Act B.E. 2518 (1975)",
            "summary": "Governs collective bargaining, trade unions, and labour dispute resolution.",
            "details": [
                "Employees have the right to form and join trade unions and employee committees.",
                "Employers cannot terminate, reduce wages, or take adverse action against union members.",
                "Labour disputes follow a defined process: negotiation, conciliation, then the Labour Relations Committee.",
                "Strikes and lockouts are permitted only after following the legal dispute resolution process.",
                "Employee committees (with 50+ employees) can negotiate working conditions with employers.",
            ],
            "what_to_do": "Contact the Department of Labour Protection and Welfare. For unfair labour practices, file a complaint with the Labour Relations Committee.",
        },
    ],
}


@router.get("/", response_class=HTMLResponse)
async def rights_overview(
    request: Request,
    country: str | None = None,
    user: User | None = Depends(get_optional_user),
):
    if country and country in RIGHTS_BY_COUNTRY:
        selected = country
    elif user and user.country in RIGHTS_BY_COUNTRY:
        selected = user.country
    else:
        selected = "us"

    categories = RIGHTS_BY_COUNTRY[selected]
    return templates.TemplateResponse(
        "rights.html",
        {
            "request": request,
            "user": user,
            "categories": categories,
            "countries": COUNTRY_NAMES,
            "selected_country": selected,
        },
    )


@router.get("/{category_id}", response_class=HTMLResponse)
async def rights_detail(
    category_id: str,
    request: Request,
    country: str | None = None,
    user: User | None = Depends(get_optional_user),
):
    if country and country in RIGHTS_BY_COUNTRY:
        selected = country
    elif user and user.country in RIGHTS_BY_COUNTRY:
        selected = user.country
    else:
        selected = "us"

    categories = RIGHTS_BY_COUNTRY[selected]
    category = next((c for c in categories if c["id"] == category_id), None)
    if not category:
        return templates.TemplateResponse(
            "404.html", {"request": request, "user": user}, status_code=404
        )
    return templates.TemplateResponse(
        "rights_detail.html",
        {
            "request": request,
            "user": user,
            "category": category,
            "selected_country": selected,
            "country_name": COUNTRY_NAMES[selected],
        },
    )

"""Employer policy drafting and generation routes."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/policies")
templates = Jinja2Templates(directory="app/templates")

POLICY_TEMPLATES = [
    {
        "id": "anti_discrimination",
        "title": "Anti-Discrimination Policy",
        "category": "Core",
        "summary": "Prohibits discrimination based on protected characteristics in all employment decisions.",
        "template": """ANTI-DISCRIMINATION POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to providing a workplace free from discrimination. This policy prohibits discrimination in all aspects of employment, including hiring, firing, compensation, promotion, training, and benefits.

2. SCOPE
This policy applies to all employees, applicants, contractors, and vendors of {company_name}.

3. PROTECTED CHARACTERISTICS
{company_name} prohibits discrimination based on race, color, religion, sex (including pregnancy, sexual orientation, and gender identity), national origin, age (40 and older), disability, genetic information, veteran status, or any other characteristic protected by applicable federal, state, or local law.

4. PROHIBITED CONDUCT
The following actions are prohibited when motivated by a protected characteristic:
- Refusing to hire or terminating an employee
- Unequal pay or benefits for substantially similar work
- Denying promotions, transfers, or training opportunities
- Segregating or classifying employees in a way that limits opportunities
- Harassing or creating a hostile work environment
- Retaliating against employees who report discrimination

5. REASONABLE ACCOMMODATIONS
{company_name} will provide reasonable accommodations for disabilities and sincerely held religious beliefs, unless doing so would cause undue hardship. Employees requesting accommodations should contact {contact_person}.

6. REPORTING PROCEDURES
Employees who experience or witness discrimination should report it promptly to:
- Their direct supervisor or manager
- Human Resources at {hr_contact}
- {contact_person}

Reports may be made verbally or in writing. Anonymous reports will be accepted and investigated to the extent possible.

7. INVESTIGATION PROCESS
All reports of discrimination will be investigated promptly, thoroughly, and impartially. {company_name} will maintain confidentiality to the extent possible. Investigations will typically include interviews with the complainant, the accused, and relevant witnesses, as well as review of any relevant documents.

8. CORRECTIVE ACTION
If an investigation confirms that discrimination has occurred, {company_name} will take prompt and appropriate corrective action, up to and including termination.

9. NO RETALIATION
{company_name} strictly prohibits retaliation against anyone who reports discrimination, participates in an investigation, or opposes discriminatory practices. Retaliation itself is a violation of this policy and will result in disciplinary action.

10. POLICY ACKNOWLEDGMENT
All employees are required to review and acknowledge this policy upon hire and annually thereafter.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
    },
    {
        "id": "anti_harassment",
        "title": "Anti-Harassment Policy",
        "category": "Core",
        "summary": "Defines and prohibits workplace harassment, including sexual harassment.",
        "template": """ANTI-HARASSMENT POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to maintaining a work environment free from harassment of any kind. This policy defines harassment, provides examples, and outlines reporting and investigation procedures.

2. SCOPE
This policy applies to all employees, supervisors, managers, executives, contractors, clients, vendors, and visitors at all {company_name} locations and company-sponsored events.

3. DEFINITION OF HARASSMENT
Harassment is unwelcome conduct based on a protected characteristic that:
- Is made a condition of employment (quid pro quo), or
- Is severe or pervasive enough to create a hostile, intimidating, or offensive work environment

4. EXAMPLES OF PROHIBITED CONDUCT
- Offensive jokes, slurs, epithets, or name-calling
- Physical assaults, threats, or intimidation
- Ridicule, mockery, insults, or put-downs
- Offensive objects, pictures, or graphics
- Unwelcome sexual advances, requests for sexual favors, or other verbal or physical conduct of a sexual nature
- Interference with an employee's work performance
- Cyber-harassment through email, social media, or messaging

5. RESPONSIBILITIES
Supervisors and managers must:
- Model respectful behavior
- Take all complaints seriously and report them to HR immediately
- Monitor the workplace for signs of harassment
- Take prompt interim action when needed to protect complainants

All employees must:
- Treat colleagues with dignity and respect
- Report harassment they experience or witness
- Cooperate fully with investigations

6. REPORTING PROCEDURES
Employees who experience or witness harassment should immediately contact:
- Their direct supervisor (unless the supervisor is the alleged harasser)
- Human Resources at {hr_contact}
- {contact_person}

Reports can be made verbally, in writing, or by email.

7. INVESTIGATION AND RESOLUTION
All complaints will be investigated promptly and impartially. Both the complainant and the accused will have an opportunity to present their account. {company_name} will take appropriate corrective action based on investigation findings.

8. NO RETALIATION
Retaliation against anyone who reports harassment or participates in an investigation is strictly prohibited and will result in disciplinary action up to and including termination.

9. TRAINING
All employees will receive harassment prevention training upon hire and annually. Supervisors and managers will receive additional training on their responsibilities.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
    },
    {
        "id": "whistleblower",
        "title": "Whistleblower & Anti-Retaliation Policy",
        "category": "Core",
        "summary": "Protects employees who report violations and prohibits retaliation.",
        "template": """WHISTLEBLOWER AND ANTI-RETALIATION POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} encourages employees to report suspected violations of law, regulation, or company policy without fear of retaliation. This policy establishes protections and procedures for such reporting.

2. SCOPE
This policy applies to all employees, officers, directors, and contractors of {company_name}.

3. PROTECTED ACTIVITY
The following activities are protected under this policy:
- Reporting suspected violations of law or company policy
- Filing a complaint with a government agency
- Participating in or cooperating with an investigation
- Refusing to participate in activities that would violate the law
- Requesting a reasonable accommodation

4. REPORTING CHANNELS
Employees may report concerns through any of the following channels:
- Direct supervisor or manager
- Human Resources at {hr_contact}
- {contact_person}
- Anonymous reporting (reports will be investigated to the extent possible)

5. CONFIDENTIALITY
{company_name} will protect the confidentiality of whistleblowers to the fullest extent possible. Information will only be shared on a need-to-know basis for investigation purposes.

6. INVESTIGATION
All reports will be reviewed and, where warranted, investigated promptly. The investigation will be conducted by qualified personnel who are independent of the matter being investigated.

7. PROHIBITED RETALIATION
{company_name} strictly prohibits retaliation in any form, including but not limited to:
- Termination or demotion
- Suspension, pay reduction, or schedule changes
- Threats, intimidation, or coercion
- Negative performance evaluations not based on merit
- Reassignment to less desirable duties or locations
- Any other adverse action motivated by the employee's protected activity

8. CONSEQUENCES
Employees who engage in retaliation will face disciplinary action up to and including termination. Managers who fail to report known retaliation will also face disciplinary action.

9. GOOD FAITH REPORTING
This policy protects employees who make reports in good faith, even if the allegation is not ultimately substantiated. However, knowingly making a false report is a violation of company policy.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
    },
    {
        "id": "wage_hour",
        "title": "Wage & Hour Policy",
        "category": "Compensation",
        "summary": "Establishes pay practices, overtime rules, and timekeeping requirements.",
        "template": """WAGE AND HOUR POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to compensating employees fairly and in full compliance with all applicable federal, state, and local wage and hour laws.

2. PAY PRACTICES
- All employees will be paid on {company_name}'s regular pay schedule
- Pay stubs will be provided with each payment, detailing hours worked, rate of pay, deductions, and net pay
- Employees must review their pay stubs promptly and report any discrepancies to {hr_contact}

3. TIMEKEEPING
- Non-exempt employees must accurately record all hours worked
- Time records must reflect actual start and stop times, including meal periods
- Employees may not work off the clock under any circumstances
- Falsifying time records is grounds for disciplinary action

4. OVERTIME
- Non-exempt employees will be paid overtime at 1.5 times their regular rate for all hours worked over 40 in a workweek
- Overtime must be approved in advance by a supervisor
- Employees may not waive their right to overtime pay

5. MEAL AND REST PERIODS
- Employees are entitled to meal and rest periods as required by applicable law
- Supervisors must ensure employees are free to take their breaks without interruption
- If an employee is required to work through a meal period, the time will be compensated

6. DEDUCTIONS
{company_name} will only make deductions from employee pay as required or permitted by law. No unauthorized deductions will be made.

7. EQUAL PAY
{company_name} is committed to pay equity. Compensation decisions are based on job duties, experience, performance, and market data — not on gender, race, or any other protected characteristic.

8. FINAL PAY
Upon separation of employment, final wages will be paid in accordance with applicable state law.

9. REPORTING CONCERNS
Employees who believe they have not been properly compensated should contact {hr_contact} or {contact_person} immediately. No employee will face retaliation for raising a pay concern.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
    },
    {
        "id": "workplace_safety",
        "title": "Workplace Safety Policy",
        "category": "Safety",
        "summary": "Outlines safety procedures, hazard reporting, and employee protections.",
        "template": """WORKPLACE SAFETY POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to providing a safe and healthy work environment for all employees, contractors, and visitors.

2. EMPLOYER RESPONSIBILITIES
{company_name} will:
- Comply with all applicable OSHA and state safety regulations
- Identify and correct workplace hazards
- Provide safety training and personal protective equipment (PPE) at no cost to employees
- Maintain records of work-related injuries and illnesses (OSHA 300 log)
- Post required safety notices in visible locations

3. EMPLOYEE RESPONSIBILITIES
Employees must:
- Follow all safety rules and procedures
- Use required PPE and safety equipment
- Report hazards, injuries, and near-misses immediately to their supervisor
- Participate in required safety training
- Not operate equipment they are not trained or authorized to use

4. HAZARD REPORTING
Employees should report safety hazards to their supervisor or to {contact_person}. Reports can be made anonymously. All reports will be investigated and addressed promptly.

5. RIGHT TO REFUSE UNSAFE WORK
Employees have the right to refuse work that they reasonably believe poses an imminent danger of death or serious physical harm. Employees exercising this right should notify their supervisor and {contact_person} immediately.

6. EMERGENCY PROCEDURES
- Emergency exits and evacuation routes are posted throughout the workplace
- Fire drills will be conducted at least annually
- First aid kits are maintained at designated locations
- Employees should call 911 for life-threatening emergencies

7. INJURY REPORTING
All work-related injuries and illnesses must be reported to a supervisor immediately, regardless of severity. {company_name} will provide access to medical treatment and file required workers' compensation paperwork.

8. NO RETALIATION
{company_name} will not retaliate against any employee who reports a safety concern, files an OSHA complaint, or exercises their right to a safe workplace.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
    },
    {
        "id": "leave_accommodations",
        "title": "Leave & Accommodations Policy",
        "category": "Leave",
        "summary": "Covers FMLA, disability accommodations, and other protected leave.",
        "template": """LEAVE AND ACCOMMODATIONS POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} complies with the Family and Medical Leave Act (FMLA), the Americans with Disabilities Act (ADA), and all applicable state and local leave laws.

2. FMLA LEAVE
Eligible employees may take up to 12 weeks of unpaid, job-protected leave per year for:
- The birth or placement of a child for adoption or foster care
- A serious health condition that prevents the employee from performing their job
- Caring for a spouse, child, or parent with a serious health condition
- Qualifying exigencies related to a family member's military service

Eligibility: Employees who have worked for {company_name} for at least 12 months and at least 1,250 hours in the preceding 12 months.

3. REQUESTING LEAVE
Employees should provide at least 30 days' notice for foreseeable leave. For unforeseeable leave, notice should be given as soon as practicable. Requests should be directed to {hr_contact}.

4. DISABILITY ACCOMMODATIONS
{company_name} will provide reasonable accommodations to qualified employees with disabilities, unless doing so would cause undue hardship. The interactive process includes:
- Employee requests accommodation (verbally or in writing)
- {company_name} and employee discuss the limitation and possible accommodations
- {company_name} selects and implements an effective accommodation

5. PREGNANCY ACCOMMODATIONS
{company_name} will provide reasonable accommodations for pregnancy, childbirth, and related medical conditions, including modified duties, schedule adjustments, and additional break time.

6. RELIGIOUS ACCOMMODATIONS
{company_name} will provide reasonable accommodations for sincerely held religious beliefs, practices, and observances, unless doing so would cause undue hardship.

7. JOB PROTECTION
Employees returning from FMLA leave or approved accommodation leave will be restored to the same or an equivalent position with equivalent pay, benefits, and terms of employment.

8. NO RETALIATION
{company_name} prohibits retaliation against employees who request or use protected leave or accommodations.

9. CONTACT
For questions about leave or accommodations, contact {hr_contact} or {contact_person}.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
    },
]


@router.get("/", response_class=HTMLResponse)
async def policies_list(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        "policies.html",
        {"request": request, "user": user, "policies": POLICY_TEMPLATES},
    )


@router.get("/{policy_id}", response_class=HTMLResponse)
async def policy_form(
    policy_id: str, request: Request, user: User = Depends(get_current_user)
):
    policy = next((p for p in POLICY_TEMPLATES if p["id"] == policy_id), None)
    if not policy:
        return RedirectResponse("/policies", status_code=303)
    return templates.TemplateResponse(
        "policy_form.html",
        {"request": request, "user": user, "policy": policy},
    )


@router.post("/{policy_id}/generate", response_class=HTMLResponse)
async def generate_policy(
    policy_id: str,
    request: Request,
    company_name: str = Form(...),
    effective_date: str = Form(""),
    contact_person: str = Form(""),
    hr_contact: str = Form(""),
    user: User = Depends(get_current_user),
):
    policy = next((p for p in POLICY_TEMPLATES if p["id"] == policy_id), None)
    if not policy:
        return RedirectResponse("/policies", status_code=303)

    rendered = policy["template"].format(
        company_name=company_name or "[Company Name]",
        effective_date=effective_date or "[Date]",
        contact_person=contact_person or "[Contact Person]",
        hr_contact=hr_contact or "[HR Contact]",
    )

    return templates.TemplateResponse(
        "policy_result.html",
        {
            "request": request,
            "user": user,
            "policy": policy,
            "rendered": rendered,
            "company_name": company_name,
        },
    )

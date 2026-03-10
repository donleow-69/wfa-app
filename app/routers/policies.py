"""Employer policy drafting and generation routes."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/policies")
templates = Jinja2Templates(directory="app/templates")

COUNTRY_NAMES = {
    "us": "United States",
    "sg": "Singapore",
    "my": "Malaysia",
    "id": "Indonesia",
    "ph": "Philippines",
    "th": "Thailand",
}

POLICY_TEMPLATES_BY_COUNTRY = {
    "us": [
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
    ],
    "sg": [
        {
            "id": "fair_employment",
            "title": "Workplace Fairness Act-Compliant Fair Employment Policy",
            "category": "Core",
            "summary": "Ensures non-discriminatory hiring and employment practices per the Workplace Fairness Act.",
            "template": """FAIR EMPLOYMENT POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to fair and merit-based employment practices in accordance with Singapore's Workplace Fairness Act and the Employment Act (Cap. 91).

2. SCOPE
This policy applies to all employees, job applicants, contractors, and agents of {company_name} in Singapore.

3. NON-DISCRIMINATION
{company_name} will not discriminate against any individual on the basis of age, race, gender, religion, marital status, family responsibilities, disability, or any other characteristic unrelated to the job. All employment decisions — including recruitment, selection, compensation, promotion, training, and termination — will be based on merit.

4. RECRUITMENT
- Job advertisements will focus on job requirements and will not state preferences for age, race, gender, language, or other non-job-related characteristics.
- Selection criteria will be based on skills, qualifications, experience, and ability to perform the job.
- Interview questions will be job-relevant and will not probe into personal characteristics.

5. COMPENSATION AND BENEFITS
{company_name} will ensure fair and equitable compensation based on job scope, competencies, and performance. Benefits will be administered without discrimination.

6. CAREER DEVELOPMENT
All employees will have equal access to training, development, and promotion opportunities based on merit and business needs.

7. FLEXIBLE WORK ARRANGEMENTS
{company_name} will consider requests for flexible work arrangements (such as flexible hours, remote work, or part-time arrangements) in accordance with the Tripartite Standard on Flexible Work Arrangements.

8. GRIEVANCE HANDLING
Employees who believe they have been subjected to discriminatory treatment should report to {contact_person} or {hr_contact}. All complaints will be investigated promptly and confidentially. No retaliation will be tolerated.

9. COMPLIANCE
This policy is aligned with the Workplace Fairness Act and the Employment Act (Cap. 91). Violations will result in disciplinary action.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "wsh_policy",
            "title": "Workplace Safety & Health Policy",
            "category": "Safety",
            "summary": "WSHA-compliant safety policy covering risk assessment and incident management.",
            "template": """WORKPLACE SAFETY AND HEALTH POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to ensuring the safety, health, and welfare of all persons at the workplace in compliance with the Workplace Safety and Health Act (WSHA) and its subsidiary legislation.

2. MANAGEMENT COMMITMENT
{company_name}'s management commits to:
- Providing a safe and healthy work environment
- Complying with all applicable WSH legislation and approved codes of practice
- Providing adequate resources for WSH management
- Reviewing and improving WSH performance continually

3. RISK MANAGEMENT
- Risk assessments will be conducted for all work activities before commencement.
- Control measures will be implemented according to the hierarchy of controls (elimination, substitution, engineering, administrative, PPE).
- Risk assessments will be reviewed regularly and whenever there are changes to work processes.

4. EMPLOYEE RESPONSIBILITIES
All employees must:
- Follow safe work procedures and instructions
- Use PPE provided and maintain it in good condition
- Report any unsafe conditions, near-misses, or incidents immediately
- Participate in WSH training programmes
- Not wilfully or recklessly endanger themselves or others

5. INCIDENT REPORTING AND INVESTIGATION
- All workplace accidents, dangerous occurrences, and occupational diseases must be reported to MOM as required under WSHA.
- Near-misses must be reported internally and investigated to prevent recurrence.
- Investigation findings will be used to improve workplace safety.

6. EMERGENCY PREPAREDNESS
- Emergency response plans are in place for fire, medical emergencies, and other foreseeable scenarios.
- Emergency drills will be conducted regularly.
- First aid facilities and trained first aiders will be available at the workplace.

7. TRAINING
All employees will receive WSH orientation upon employment and ongoing training relevant to their work. Persons performing hazardous work will receive specialised training.

8. NO RETALIATION
No employee will be penalised for reporting WSH concerns in good faith.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "anti_harassment_sg",
            "title": "Anti-Harassment Policy (POHA-Aligned)",
            "category": "Core",
            "summary": "Prohibits workplace harassment and bullying in compliance with Singapore's POHA.",
            "template": """ANTI-HARASSMENT AND ANTI-BULLYING POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to providing a workplace free from harassment and bullying. This policy is aligned with the Protection from Harassment Act (POHA) and the Tripartite Advisory on Managing Workplace Harassment.

2. SCOPE
This policy covers all forms of harassment — verbal, physical, visual, and cyber — occurring in the workplace or in connection with work (including business trips, work events, and online communications).

3. DEFINITION
Harassment includes any threatening, abusive, or insulting behaviour or communication that causes or is likely to cause harassment, alarm, or distress. This includes but is not limited to:
- Verbal abuse, threats, or intimidation
- Offensive or derogatory comments about a person's characteristics
- Unwelcome sexual advances or sexually suggestive behaviour
- Cyberbullying or online harassment related to work
- Stalking or repeated unwanted contact
- Humiliation, ostracism, or spreading malicious rumours

4. EMPLOYER OBLIGATIONS
{company_name} will:
- Take all complaints of harassment seriously and investigate promptly
- Protect complainants from retaliation
- Take appropriate disciplinary action against perpetrators
- Implement measures to prevent workplace harassment

5. EMPLOYEE OBLIGATIONS
All employees must:
- Treat colleagues, clients, and business contacts with respect
- Refrain from any form of harassment or bullying
- Report incidents of harassment they witness or experience

6. REPORTING
Reports of harassment should be made to {contact_person} or {hr_contact}. Reports will be treated confidentially and investigated promptly.

7. REMEDIES
Under POHA, victims of harassment may apply for Protection Orders or Expedited Protection Orders from the Protection from Harassment Court. {company_name} supports employees in exercising their legal rights.

8. DISCIPLINARY ACTION
Employees found to have engaged in harassment will face disciplinary action up to and including termination.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "pdpa_policy",
            "title": "Data Protection Policy (PDPA-Compliant)",
            "category": "Data Protection",
            "summary": "Employee data protection policy compliant with Singapore's Personal Data Protection Act.",
            "template": """EMPLOYEE DATA PROTECTION POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to protecting the personal data of employees, job applicants, and other individuals in compliance with the Personal Data Protection Act 2012 (PDPA).

2. DATA PROTECTION OFFICER
{company_name}'s Data Protection Officer (DPO) is {contact_person}, who can be reached at {hr_contact}.

3. COLLECTION OF PERSONAL DATA
{company_name} collects personal data (such as name, NRIC/FIN, contact details, employment history, and financial information) only for purposes that are reasonable and necessary for employment, including:
- Recruitment and onboarding
- Payroll and benefits administration
- Performance management
- Compliance with legal obligations (e.g., CPF, tax, MOM reporting)

4. CONSENT
{company_name} will obtain consent before collecting, using, or disclosing personal data, except where permitted by law (e.g., for contractual necessity or legal compliance).

5. USE AND DISCLOSURE
Personal data will only be used for the purposes for which it was collected or for purposes that the individual would reasonably expect. Data will not be disclosed to third parties without consent unless required by law.

6. DATA PROTECTION MEASURES
{company_name} implements reasonable security arrangements to protect personal data, including:
- Access controls and authentication
- Encryption of sensitive data
- Regular security assessments
- Employee training on data protection

7. RETENTION AND DISPOSAL
Personal data will be retained only as long as necessary for the purposes for which it was collected or as required by law. Data that is no longer needed will be securely destroyed.

8. ACCESS AND CORRECTION
Employees may request access to their personal data held by {company_name} and request corrections. Requests should be directed to {contact_person}.

9. DATA BREACH MANAGEMENT
In the event of a data breach, {company_name} will notify the Personal Data Protection Commission (PDPC) and affected individuals as required by the PDPA.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "employment_terms_sg",
            "title": "Employment Terms & Conditions Policy",
            "category": "Core",
            "summary": "Employment Act compliance covering wages, working hours, overtime, rest days, leave entitlements, itemised payslips, and key employment terms.",
            "template": """EMPLOYMENT TERMS AND CONDITIONS POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} establishes this policy to ensure that all employment terms and conditions comply with the Employment Act (Cap. 91) and related subsidiary legislation in Singapore.

2. SCOPE
This policy applies to all employees of {company_name} covered under the Employment Act, including full-time, part-time, and contract employees. Managers and executives earning above the salary threshold are covered for core provisions (payment of salary, hours of work, and related matters) as amended.

3. KEY EMPLOYMENT TERMS (KET)
In accordance with the Employment Act, {company_name} will provide every employee with written key employment terms within 14 days of the start of employment. KET includes:
- Full name of employer and employee
- Job title, main duties, and responsibilities
- Start date of employment and duration (if fixed-term)
- Working arrangements (hours of work, rest days, number of working days per week)
- Salary period, basic salary, fixed allowances, fixed deductions, overtime payment period, and overtime rate of pay
- Types of leave (annual leave, outpatient sick leave, hospitalisation leave, maternity/paternity/childcare leave)
- Other employment terms (probation period, notice period, place of work)

4. WAGES
- Wages will be paid at least once a month, within 7 days after the end of the salary period.
- Authorised deductions will not exceed 50% of wages in any one salary period (excluding deductions for absence, accommodation, and income tax).
- {company_name} will not make unauthorised deductions from employee wages.

5. ITEMISED PAYSLIPS
{company_name} will provide itemised payslips to all employees for each salary payment. Payslips will include:
- Employer and employee name
- Date of payment and salary period
- Basic salary, allowances, and additional payments (overtime, bonus, rest day/public holiday pay)
- Deductions itemised by type
- Net salary paid
- Start and end dates of the overtime payment period, overtime hours worked, and overtime pay (for employees entitled to overtime)

6. WORKING HOURS AND OVERTIME
- Normal working hours shall not exceed 8 hours per day or 44 hours per week.
- Employees covered under Part IV of the Employment Act are entitled to overtime pay at 1.5 times the hourly basic rate for work exceeding normal hours.
- Overtime is capped at 72 hours per month.
- {company_name} will maintain accurate records of hours worked.

7. REST DAYS
Every employee is entitled to 1 rest day per week without pay, or 2 rest days per week at {company_name}'s discretion. Work on a rest day requires employee consent (except in certain circumstances) and is compensated at the applicable rates.

8. PUBLIC HOLIDAYS
Employees are entitled to 11 gazetted public holidays per year with pay. If required to work on a public holiday, employees will receive an additional day's salary or a replacement day off.

9. LEAVE ENTITLEMENTS
- Annual leave: 7 days for the first year, increasing by 1 day per year to a maximum of 14 days.
- Outpatient sick leave: 14 days per year (with medical certificate).
- Hospitalisation leave: 60 days per year (inclusive of outpatient sick leave entitlement).
- Maternity leave: 16 weeks for eligible employees (Government-Paid Maternity Leave under GPML scheme).
- Paternity leave: 2 weeks (Government-Paid Paternity Leave).
- Childcare leave: 6 days per year for employees with children under 7.
- Extended childcare leave: 2 days per year for employees with children aged 7-12.

10. TERMINATION AND NOTICE
- Notice periods will be as specified in the employment contract.
- In the absence of contractual terms, statutory notice periods apply (1 day to 4 weeks depending on length of service).
- Termination with cause (misconduct) must follow the inquiry process under the Employment Act.

11. EMPLOYER COMPLIANCE CUSTOMISATION
{company_name} may, at its discretion, provide terms more favourable than the statutory minimums. Departments and business units may establish supplementary guidelines, subject to approval by {contact_person}, provided they meet or exceed the standards set out in this policy and the Employment Act.

12. CONTACT
For questions about employment terms and conditions, contact {hr_contact} or {contact_person}.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "foreign_worker_sg",
            "title": "Foreign Worker Management Policy",
            "category": "Compliance",
            "summary": "EFMA compliance covering valid work passes, salary protections, accommodation standards, medical coverage, and no passport retention.",
            "template": """FOREIGN WORKER MANAGEMENT POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to responsible and lawful employment of foreign workers in Singapore, in full compliance with the Employment of Foreign Manpower Act (EFMA) and conditions imposed by the Ministry of Manpower (MOM).

2. SCOPE
This policy applies to the management of all foreign employees of {company_name} holding Work Permits, S Passes, Employment Passes, or any other work pass issued by MOM.

3. VALID WORK PASSES
- {company_name} will ensure that every foreign employee holds a valid work pass before commencing work.
- {company_name} will not deploy foreign workers in occupations or at locations not permitted by their work pass conditions.
- Work pass applications and renewals will be submitted in a timely manner to avoid lapses.
- {company_name} will monitor work pass expiry dates and initiate renewals or cancellations as required.

4. SALARY PROTECTIONS
- {company_name} will pay foreign employees the salary declared in the work pass application, on time and in full.
- No salary deductions, kickbacks, or recovery of recruitment costs from foreign employees will be permitted.
- Foreign employees will not be required to pay for their own work pass fees, levy, or security bond.
- All salary payments will be properly documented with itemised payslips.

5. NO PASSPORT RETENTION
- {company_name} strictly prohibits the retention of any foreign employee's passport, travel documents, or work pass.
- All personal documents will remain in the possession of the foreign employee at all times.
- Any request by a supervisor or manager to hold an employee's documents is a violation of this policy and the EFMA.

6. ACCOMMODATION
- Where {company_name} provides or arranges accommodation for foreign workers, the accommodation must meet MOM's standards for acceptable accommodation.
- Accommodation must be safe, clean, and provide adequate living space, ventilation, sanitation, and cooking facilities.
- {company_name} will conduct regular inspections to ensure continued compliance with accommodation standards.

7. MEDICAL COVERAGE
- {company_name} will purchase and maintain medical insurance for all Work Permit and S Pass holders as required by MOM.
- Foreign employees will have access to medical treatment and will not be made to bear the cost of medical insurance.
- {company_name} will ensure that employees who are injured or fall ill receive appropriate medical attention.

8. UPKEEP AND MAINTENANCE
- {company_name} will bear the costs of the foreign employee's upkeep and maintenance during the employment period.
- Foreign employees will not be made to bear the costs of repatriation.

9. COMPLIANCE CHECKS AND CUSTOMISATION
{company_name} will maintain a compliance monitoring schedule tailored to the nature and scale of its foreign workforce. Each department or business unit may define supplementary compliance procedures, subject to approval by {contact_person}, provided they meet the standards of this policy and the EFMA. Compliance checks will include:
- Quarterly review of work pass validity and conditions
- Annual audit of salary records against declared amounts
- Regular accommodation inspections (where applicable)
- Periodic review of medical insurance coverage
- Assessment of recruitment practices for compliance with anti-kickback provisions

10. REPORTING AND ENFORCEMENT
Any employee who becomes aware of a violation of this policy or the EFMA must report it immediately to {contact_person} or {hr_contact}. Violations may result in disciplinary action up to and including termination. {company_name} may also be subject to penalties under the EFMA, including fines, debarment from hiring foreign workers, and criminal prosecution.

11. REPATRIATION
Upon cancellation of the work pass or termination of employment, {company_name} will arrange and bear the cost of repatriation of the foreign employee to their country of origin.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
    ],
    "my": [
        {
            "id": "sexual_harassment_my",
            "title": "Sexual Harassment Policy (EA s81H)",
            "category": "Core",
            "summary": "Anti-sexual harassment policy compliant with Employment Act 1955 Section 81H.",
            "template": """SEXUAL HARASSMENT POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to providing a workplace free from sexual harassment, in compliance with Section 81H of the Employment Act 1955 and the Employment (Amendment) Act 2022.

2. SCOPE
This policy applies to all employees, contractors, clients, and visitors at all {company_name} locations and work-related events in Malaysia.

3. DEFINITION
Sexual harassment means any unwanted conduct of a sexual nature, whether verbal, non-verbal, visual, gestural, or physical, directed at a person which is offensive, humiliating, or a threat to their well-being. This includes:
- Unwelcome sexual advances or requests for sexual favours
- Sexually suggestive comments, jokes, or innuendos
- Display of offensive or pornographic materials
- Unwanted physical contact of a sexual nature
- Sexual messages or images via electronic means

4. EMPLOYER DUTIES (SECTION 81H)
Under the Employment Act, {company_name} is required to:
- Display a conspicuous notice on sexual harassment at the workplace
- Inquire into complaints of sexual harassment in a prescribed manner
- Take appropriate action based on findings

5. COMPLAINT PROCEDURE
a) An employee who experiences sexual harassment should lodge a complaint with {contact_person} or {hr_contact}.
b) The complaint should be made in writing, detailing the incident(s).
c) {company_name} will conduct an inquiry within 30 days of receiving the complaint.
d) Both the complainant and the alleged harasser will be given the opportunity to be heard.

6. INVESTIGATION
An internal committee will investigate all complaints promptly and impartially, maintaining confidentiality to the extent possible.

7. DISCIPLINARY ACTION
If the inquiry finds that sexual harassment occurred, {company_name} will take appropriate disciplinary action, which may include warning, suspension, demotion, or termination.

8. PROTECTION AGAINST RETALIATION
No employee will be penalised for reporting sexual harassment in good faith. Retaliation is a separate disciplinary offence.

9. EXTERNAL REMEDIES
Employees may also lodge a complaint with the Director General of Labour under the Employment Act.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "osh_policy_my",
            "title": "Occupational Safety & Health Policy (OSHA 1994)",
            "category": "Safety",
            "summary": "Workplace safety policy compliant with Malaysia's Occupational Safety and Health Act 1994.",
            "template": """OCCUPATIONAL SAFETY AND HEALTH POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to providing a safe and healthy work environment in compliance with the Occupational Safety and Health Act 1994 (OSHA 1994) and its subsidiary regulations.

2. MANAGEMENT COMMITMENT
{company_name} management is committed to:
- Ensuring the safety, health, and welfare of all employees
- Providing and maintaining safe plant, systems of work, and work environment
- Providing information, instruction, training, and supervision for safe work
- Allocating adequate resources for safety and health

3. SAFETY AND HEALTH COMMITTEE
In accordance with OSHA 1994, {company_name} maintains a Safety and Health Committee comprising management and employee representatives. The committee meets regularly to review safety performance and recommend improvements.

4. RISK ASSESSMENT
- Hazard identification and risk assessments will be conducted for all work activities.
- Risk control measures will be implemented and reviewed regularly.
- Chemical health risk assessments will be conducted as required under USECHH Regulations 2000.

5. EMPLOYEE DUTIES
Under OSHA 1994, all employees must:
- Take reasonable care for their own safety and health and that of others
- Cooperate with the employer on safety and health matters
- Use PPE provided and follow safe work procedures
- Report hazards, incidents, and near-misses immediately

6. INCIDENT REPORTING
All accidents, dangerous occurrences, and occupational diseases must be reported to DOSH as required by the Notification of Accident, Dangerous Occurrence, Occupational Poisoning and Occupational Disease (NADOPOD) Regulations.

7. EMERGENCY PROCEDURES
Emergency response plans, including evacuation procedures and assembly points, are in place and communicated to all employees.

8. TRAINING
All employees will receive OSH induction training and ongoing training relevant to workplace hazards.

9. REVIEW
This policy will be reviewed annually and updated as needed to ensure continued compliance and effectiveness.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "employment_policy_my",
            "title": "Employment Policy (EA 1955)",
            "category": "Core",
            "summary": "Employment Act 1955 compliance covering working hours, overtime, leave entitlements including maternity (98 days) and paternity (7 days), and flexible working arrangements under the 2022/2023 amendments.",
            "template": """EMPLOYMENT POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
This policy establishes the employment terms and conditions at {company_name} in compliance with the Employment Act 1955 (EA 1955) as amended by the Employment (Amendment) Act 2022.

2. SCOPE
This policy applies to all employees of {company_name} in Malaysia. Following the 2022 amendment, the Employment Act now covers all employees regardless of wage level for core protections.

3. WORKING HOURS
- Maximum normal working hours: 45 hours per week (reduced from 48 hours under the 2022 amendment).
- Daily working hours shall not exceed 8 hours, or such hours as agreed under a flexible working arrangement.
- Rest period of at least 30 minutes after 5 consecutive hours of work.
- At least 1 rest day per week.

4. OVERTIME
- Overtime is payable for work exceeding normal hours of work, at the following rates:
  - Normal working day: 1.5 times the hourly rate of pay
  - Rest day: 2.0 times the hourly rate of pay (for work exceeding normal hours)
  - Public holiday: 3.0 times the hourly rate of pay
- Maximum overtime: 104 hours per month.

5. WAGES
- All employees will be paid at least the applicable minimum wage.
- Wages must be paid no later than the 7th day after the last day of the salary period.
- {company_name} will not make unauthorised deductions from wages.

6. LEAVE ENTITLEMENTS
- Annual leave:
  - Less than 2 years of service: 8 days
  - 2 to 5 years: 12 days
  - More than 5 years: 16 days
- Sick leave (without hospitalisation):
  - Less than 2 years: 14 days
  - 2 to 5 years: 18 days
  - More than 5 years: 22 days
- Hospitalisation leave: 60 days per year (inclusive of non-hospitalisation sick leave).
- Maternity leave: 98 days with pay for female employees (increased from 60 days under the 2022 amendment). Eligibility: employed for at least 90 days in the 9 months before confinement and fewer than 5 surviving children.
- Paternity leave: 7 consecutive days with pay for married male employees (new entitlement under the 2022 amendment).
- Public holidays: 11 gazetted public holidays per year, including at least 5 compulsory holidays (National Day, Yang di-Pertuan Agong's Birthday, Ruler's Birthday, Workers' Day, Malaysia Day).

7. FLEXIBLE WORKING ARRANGEMENTS (2022/2023 AMENDMENT)
- Employees may apply in writing to {company_name} for flexible working arrangements relating to:
  - Hours of work (flexible start/end times)
  - Days of work (compressed work week)
  - Place of work (remote or hybrid working)
- {company_name} will approve or refuse the application within 60 days with written reasons if refused.

8. TERMINATION AND NOTICE
- Notice periods as stipulated in the employment contract.
- Statutory minimum notice periods:
  - Less than 2 years of service: 4 weeks
  - 2 to 5 years: 6 weeks
  - More than 5 years: 8 weeks
- Either party may pay wages in lieu of notice.

9. EMPLOYER COMPLIANCE CUSTOMISATION
{company_name} may establish additional employment standards that exceed the statutory minimums. Departments may implement supplementary procedures tailored to their operations, subject to approval by {contact_person}, provided they comply with the EA 1955 and applicable regulations.

10. CONTACT
For questions regarding employment terms, contact {hr_contact} or {contact_person}.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "anti_discrimination_my",
            "title": "Anti-Discrimination & Fair Employment Policy",
            "category": "Core",
            "summary": "Equal opportunity principles covering fair hiring, non-discrimination based on race, religion, gender, and disability, aligned with Industrial Relations Act 1967 unfair dismissal protections.",
            "template": """ANTI-DISCRIMINATION AND FAIR EMPLOYMENT POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to fair and equitable employment practices. This policy establishes non-discrimination and equal opportunity standards in alignment with Malaysian employment law, including the Federal Constitution (Article 8 — equality before the law), the Industrial Relations Act 1967, and the Persons with Disabilities Act 2008.

2. SCOPE
This policy applies to all employees, job applicants, contractors, and agents of {company_name} in Malaysia. It covers all aspects of employment, including recruitment, selection, compensation, promotion, training, transfers, and termination.

3. NON-DISCRIMINATION
{company_name} prohibits discrimination in employment on the basis of:
- Race or ethnic origin
- Religion or belief
- Gender or sexual identity
- Age
- Disability
- Marital or family status
- Political opinion
- Place of origin or nationality (subject to immigration requirements)
- Any other characteristic unrelated to job performance

4. FAIR RECRUITMENT AND SELECTION
- Job advertisements will focus on job-related qualifications and requirements.
- Selection criteria will be based on merit — skills, qualifications, experience, and ability to perform the job.
- Interview questions will be relevant to the position and will not probe into personal characteristics.
- {company_name} will not impose discriminatory requirements such as specifying age, gender, ethnicity, or marital status in job postings.

5. EQUAL OPPORTUNITY IN EMPLOYMENT
- Compensation, benefits, and career development opportunities will be based on job scope, competencies, qualifications, and performance.
- All employees will have equal access to training, mentoring, and promotion opportunities.
- {company_name} will provide reasonable accommodations for employees with disabilities, consistent with the Persons with Disabilities Act 2008.

6. PROTECTION AGAINST UNFAIR DISMISSAL
In accordance with the Industrial Relations Act 1967:
- No employee will be dismissed without just cause or excuse.
- Dismissals motivated by discrimination constitute unfair dismissal.
- Employees who believe they have been unfairly dismissed may file a complaint with the Director General of Industrial Relations within 60 days.

7. PREVENTION OF WORKPLACE BULLYING
{company_name} will not tolerate bullying, intimidation, or victimisation based on any protected characteristic. All employees are expected to treat colleagues with dignity and respect.

8. GRIEVANCE MECHANISM
Employees who believe they have been subjected to discrimination or unfair treatment should report the matter to {contact_person} or {hr_contact}. All complaints will be investigated promptly, confidentially, and impartially. No employee will face retaliation for making a complaint in good faith.

9. COMPLIANCE CUSTOMISATION
{company_name} recognises that different business units may operate in varying contexts. Each department may develop supplementary fair employment guidelines, subject to approval by {contact_person}, that address specific operational needs while maintaining the standards of this policy and applicable law.

10. TRAINING AND AWARENESS
All employees will receive training on fair employment practices. Managers and supervisors will receive additional training on preventing discrimination and handling complaints.

11. DISCIPLINARY ACTION
Violations of this policy will result in disciplinary action up to and including termination.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "foreign_worker_my",
            "title": "Foreign Worker Management Policy",
            "category": "Compliance",
            "summary": "Immigration Act compliance covering work permits, no passport retention (Passport Act 1966), SOCSO/medical coverage, and anti-trafficking obligations (ATIPSOM 2007).",
            "template": """FOREIGN WORKER MANAGEMENT POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to the lawful and ethical employment of foreign workers in Malaysia. This policy ensures compliance with the Immigration Act 1959/63, the Passport Act 1966, the Employment Act 1955, the Anti-Trafficking in Persons and Anti-Smuggling of Migrants Act 2007 (ATIPSOM), and related regulations.

2. SCOPE
This policy applies to the management of all foreign employees of {company_name} in Malaysia, including holders of Employment Passes, Visit Passes (Temporary Employment), and other work authorisations.

3. VALID WORK AUTHORISATION
- {company_name} will ensure that every foreign worker holds a valid work permit or pass before commencing employment.
- Foreign workers will only be deployed in roles and sectors authorised by their work permit.
- {company_name} will monitor permit expiry dates and ensure timely renewals or cancellations.
- Employment of undocumented or illegal workers is strictly prohibited and constitutes a criminal offence under the Immigration Act.

4. NO PASSPORT RETENTION
- Under the Passport Act 1966, it is an offence to retain or withhold another person's passport or travel document without lawful authority.
- {company_name} strictly prohibits the retention of any foreign worker's passport, travel documents, or personal identification.
- All personal documents must remain in the worker's possession at all times.
- Supervisors or managers who request to hold a foreign worker's documents will face disciplinary action.
- {company_name} will provide secure personal storage facilities so workers can safely store their own documents.

5. FAIR RECRUITMENT AND NO EXPLOITATION
- {company_name} will not charge foreign workers any recruitment fees or costs.
- Workers will not be required to repay recruitment costs, transportation, or levy charges through salary deductions or debt bondage arrangements.
- {company_name} will verify that labour supply agencies used do not engage in exploitative practices.
- These provisions are aligned with ATIPSOM 2007 anti-trafficking obligations.

6. WAGES AND EMPLOYMENT TERMS
- Foreign workers will be paid at least the applicable minimum wage, on time and in full.
- Employment contracts will be provided in a language the worker can understand.
- {company_name} will not make unauthorised deductions from foreign workers' wages.
- All payments will be documented with itemised payslips.

7. SOCIAL SECURITY AND MEDICAL COVERAGE
- Foreign workers will be registered with SOCSO (Social Security Organisation) as required.
- {company_name} will maintain valid medical insurance coverage or provide equivalent medical benefits.
- Workers who are injured or fall ill will receive appropriate medical attention and will not be penalised.

8. ACCOMMODATION
Where {company_name} provides accommodation for foreign workers, it must meet minimum standards for safety, hygiene, space, ventilation, and sanitation as required by applicable regulations.

9. COMPLIANCE MONITORING AND CUSTOMISATION
{company_name} will conduct regular compliance audits of its foreign worker management practices. Each business unit may define supplementary compliance procedures tailored to their workforce composition and operational context, subject to approval by {contact_person}, provided they meet the requirements of this policy and all applicable laws. Compliance monitoring will include:
- Quarterly review of work permit validity
- Annual audit of salary records
- Periodic accommodation inspections (where applicable)
- Assessment of recruitment agency practices
- Review of passport and document retention practices

10. ANTI-TRAFFICKING OBLIGATIONS
{company_name} is committed to preventing trafficking in persons and forced labour in accordance with ATIPSOM 2007. Indicators of trafficking include:
- Restriction of movement or confinement
- Retention of identity documents
- Debt bondage or withholding of wages
- Threats, intimidation, or physical harm
Any employee who suspects trafficking or forced labour must report it immediately to {contact_person} or {hr_contact}. Reports may also be made to the relevant authorities.

11. REPATRIATION
Upon termination or expiry of employment, {company_name} will ensure the orderly and lawful repatriation of foreign workers.

12. REPORTING AND ENFORCEMENT
Violations of this policy will result in disciplinary action up to and including termination. {company_name} may also face penalties under the Immigration Act, ATIPSOM, and other applicable laws.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
    ],
    "id": [
        {
            "id": "employment_policy_id",
            "title": "Employment Policy (Omnibus Law Compliant)",
            "category": "Core",
            "summary": "Core employment policy aligned with Indonesia's Omnibus Law on Job Creation.",
            "template": """EMPLOYMENT POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
This policy sets out the employment terms and conditions at {company_name} in compliance with Law No. 6/2023 (Omnibus Law on Job Creation) and Law No. 13/2003 (Manpower Act).

2. EMPLOYMENT CONTRACTS
- All employees will receive a written employment contract specifying terms, conditions, rights, and obligations.
- Fixed-term contracts (PKWT) will comply with maximum duration limits.
- Permanent employees (PKWTT) are entitled to full statutory protections.

3. WORKING HOURS AND OVERTIME
- Normal working hours: 7 hours/day and 40 hours/week (6-day week) or 8 hours/day and 40 hours/week (5-day week).
- Overtime is limited to 4 hours/day and 18 hours/week.
- Overtime compensation: 1.5x hourly wage for the first hour, 2x for subsequent hours.
- Overtime on rest days and public holidays is compensated at higher rates as prescribed by law.

4. WAGES
- All employees will be paid at least the applicable provincial/district minimum wage.
- Wages will be paid in Indonesian Rupiah on a regular schedule.
- {company_name} will make required social security contributions (BPJS Ketenagakerjaan and BPJS Kesehatan).

5. LEAVE ENTITLEMENTS
- Annual leave: minimum 12 working days after 12 months of continuous service.
- Maternity leave: 3 months (1.5 months before and after birth) with full pay.
- Menstrual leave: as prescribed by law for female employees experiencing pain.
- Sick leave, bereavement leave, and other statutory leave as required.

6. TERMINATION AND SEVERANCE
- Termination must be based on valid grounds as specified by law.
- Severance pay, service appreciation pay, and compensation for entitlements will be paid as required.
- Termination disputes will be resolved through bipartite negotiation, mediation, and if necessary, the Industrial Relations Court.

7. NON-DISCRIMINATION
{company_name} provides equal employment opportunities regardless of gender, ethnicity, race, religion, or political views.

8. REPORTING CONCERNS
Employees may report concerns to {contact_person} or {hr_contact}.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "safety_policy_id",
            "title": "Workplace Safety Policy",
            "category": "Safety",
            "summary": "Occupational safety and health policy for Indonesian workplaces.",
            "template": """WORKPLACE SAFETY AND HEALTH POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to maintaining a safe and healthy workplace in accordance with Law No. 1/1970 on Work Safety and applicable occupational health and safety regulations.

2. EMPLOYER OBLIGATIONS
{company_name} will:
- Provide a safe workplace free from hazards
- Conduct workplace inspections and risk assessments
- Provide safety training and PPE at no cost to employees
- Report workplace accidents to the relevant authorities
- Maintain an Occupational Safety and Health Management System (SMK3) where required

3. EMPLOYEE OBLIGATIONS
All employees must:
- Follow established safety procedures
- Use PPE and safety equipment as required
- Report hazards, accidents, and near-misses immediately
- Participate in safety training

4. SOCIAL SECURITY
All employees are enrolled in BPJS Ketenagakerjaan, which covers:
- Work accident insurance (JKK)
- Death benefit (JKM)
- Old age savings (JHT)
- Pension (JP)

5. INCIDENT RESPONSE
Workplace accidents will be reported and investigated promptly. Injured workers are entitled to medical treatment and compensation under BPJS.

6. CONTACT
For safety concerns, contact {contact_person} or {hr_contact}.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "anti_discrimination_id",
            "title": "Anti-Discrimination & Equal Opportunity Policy",
            "category": "Core",
            "summary": "Manpower Act Article 5-6 non-discrimination provisions, equal treatment regardless of gender, ethnicity, race, or religion, and women's protections including maternity leave, menstrual leave, and night work regulations.",
            "template": """ANTI-DISCRIMINATION AND EQUAL OPPORTUNITY POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to equal opportunity and non-discrimination in the workplace. This policy implements the non-discrimination provisions of Law No. 13/2003 (Manpower Act), particularly Articles 5 and 6, and Law No. 6/2023 (Omnibus Law on Job Creation).

2. SCOPE
This policy applies to all employees, job applicants, contractors, and agents of {company_name} in Indonesia. It covers all aspects of employment including recruitment, compensation, promotion, training, and termination.

3. NON-DISCRIMINATION (ARTICLES 5 AND 6)
In accordance with the Manpower Act:
- Article 5: Every worker has equal opportunity to obtain employment without discrimination.
- Article 6: Every worker has the right to receive equal treatment without discrimination from the employer.
- {company_name} prohibits discrimination on the basis of:
  - Gender or sexual identity
  - Ethnicity or ethnic origin
  - Race
  - Religion or belief
  - Skin colour
  - Political views
  - Disability
  - Any other characteristic unrelated to job qualifications

4. FAIR RECRUITMENT AND SELECTION
- Job postings will focus on qualifications and job requirements.
- Selection decisions will be based on merit — skills, qualifications, experience, and competencies.
- {company_name} will not impose discriminatory criteria in recruitment.
- Interview processes will be fair, consistent, and job-relevant.

5. EQUAL COMPENSATION
- Employees performing substantially similar work will receive equal compensation regardless of gender, ethnicity, race, or other protected characteristics.
- Compensation differences will be based solely on objective factors such as experience, qualifications, performance, and job complexity.

6. WOMEN'S PROTECTIONS
The Manpower Act provides specific protections for female employees, which {company_name} fully observes:
a) Maternity leave: 3 months (1.5 months before and 1.5 months after childbirth) with full pay, or as adjusted by a doctor's recommendation. In case of miscarriage, 1.5 months of leave with pay.
b) Menstrual leave: Female employees who experience pain during menstruation and notify the employer are not obligated to work on the first and second day of menstruation, as provided under Article 81.
c) Breastfeeding: Female employees are entitled to reasonable opportunity and facilities to breastfeed during working hours, as required by the Manpower Act.
d) Night work (23:00 to 07:00): Female employees under 18 are prohibited from night work. Employers who deploy female employees during night hours must:
   - Provide nutritious food and drink
   - Maintain safety, decency, and morality in the workplace
   - Provide transportation to and from the workplace
   - Not employ pregnant women whose health would be at risk (per doctor's certificate)

7. DISABILITY INCLUSION
{company_name} will provide reasonable accommodations for employees with disabilities, consistent with Law No. 8/2016 on Persons with Disabilities. Qualified individuals with disabilities will be considered for employment on an equal basis with other candidates.

8. PREVENTION OF HARASSMENT
{company_name} does not tolerate harassment or bullying based on any protected characteristic. All employees are expected to treat colleagues with dignity and respect.

9. GRIEVANCE MECHANISM
Employees who experience or witness discrimination should report the matter to {contact_person} or {hr_contact}. All complaints will be investigated promptly and confidentially. No employee will face retaliation for making a good-faith complaint.

10. COMPLIANCE CUSTOMISATION
{company_name} recognises that different business units may have varying operational contexts. Departments may develop supplementary equal opportunity guidelines, subject to approval by {contact_person}, that address specific operational needs while meeting or exceeding the standards of this policy and applicable law.

11. DISCIPLINARY ACTION
Violations of this policy will result in disciplinary action up to and including termination.

12. DISPUTE RESOLUTION
Discrimination disputes may be resolved through bipartite negotiation, mediation, or the Industrial Relations Court, in accordance with Law No. 2/2004 on Industrial Relations Dispute Settlement.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "bpjs_compliance_id",
            "title": "Social Security (BPJS) Compliance Policy",
            "category": "Compliance",
            "summary": "BPJS Ketenagakerjaan (JKK, JKM, JHT, JP) and BPJS Kesehatan enrollment obligations, contribution rates, and worker entitlements under Law No. 24/2011 and Law No. 40/2004.",
            "template": """SOCIAL SECURITY (BPJS) COMPLIANCE POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to fulfilling its social security obligations under Law No. 24/2011 on Social Security Administering Bodies (BPJS) and Law No. 40/2004 on the National Social Security System (SJSN). This policy establishes procedures for enrollment, contributions, and benefit administration.

2. SCOPE
This policy applies to all employees of {company_name} in Indonesia, including permanent (PKWTT) and fixed-term (PKWT) employees. Employers are legally required to enroll all employees in both BPJS Ketenagakerjaan and BPJS Kesehatan programmes.

3. BPJS KETENAGAKERJAAN (EMPLOYMENT SOCIAL SECURITY)
{company_name} will enroll all employees in the following BPJS Ketenagakerjaan programmes:

a) Jaminan Kecelakaan Kerja (JKK) — Work Accident Insurance
   - Covers medical expenses, rehabilitation, compensation for disability, and death benefits resulting from work accidents or occupational diseases.
   - Contribution: Paid entirely by {company_name}, ranging from 0.24% to 1.74% of monthly wages depending on the level of work risk.
   - Coverage includes accidents during commute to/from work.

b) Jaminan Kematian (JKM) — Death Benefit
   - Provides benefits to the family/heirs of an employee who dies not due to a work accident.
   - Contribution: 0.30% of monthly wages, paid entirely by {company_name}.
   - Benefits include funeral costs and a lump-sum payment to heirs.

c) Jaminan Hari Tua (JHT) — Old Age Savings
   - A savings programme where accumulated contributions are paid to the employee upon reaching retirement age, disability, or other qualifying events.
   - Contribution: 5.7% of monthly wages (3.7% paid by {company_name}, 2.0% paid by the employee).
   - Employees may claim JHT benefits upon reaching age 56, or earlier in case of resignation (after waiting period), termination, or permanent disability.

d) Jaminan Pensiun (JP) — Pension
   - Provides monthly pension benefits for employees who have contributed for a minimum qualifying period.
   - Contribution: 3.0% of monthly wages (2.0% paid by {company_name}, 1.0% paid by the employee), subject to a maximum wage ceiling as determined by the government.
   - Benefits include old-age pension, disability pension, survivor's pension, and funeral benefit.

4. BPJS KESEHATAN (NATIONAL HEALTH INSURANCE)
- {company_name} will enroll all employees and their eligible family members (spouse and up to 3 children) in BPJS Kesehatan.
- Contribution: 5.0% of monthly wages (4.0% paid by {company_name}, 1.0% paid by the employee), subject to a maximum wage ceiling.
- Coverage includes outpatient and inpatient care, maternity services, and other healthcare services as determined by BPJS Kesehatan.
- Employees may add family members beyond the covered 3 children by paying additional contributions.

5. ENROLLMENT PROCEDURES
- {company_name} will register all new employees with BPJS Ketenagakerjaan and BPJS Kesehatan within 30 days of commencement of employment.
- {company_name} will ensure that each employee receives their BPJS membership card/number.
- Changes in employee data (salary changes, family status) will be reported to BPJS promptly.

6. CONTRIBUTION PAYMENT
- {company_name} will calculate and remit all employer and employee contributions to BPJS accurately and on time (by the 15th of each month).
- Employee contributions will be deducted from wages with proper documentation.
- Contribution records will be maintained and available for employee review.

7. EMPLOYEE ENTITLEMENTS AND CLAIMS
Employees are entitled to claim benefits under each programme as prescribed by law. {company_name} will:
- Assist employees in understanding their BPJS entitlements
- Facilitate the claims process for work accidents, death benefits, and other events
- Provide necessary documentation for JHT withdrawals and pension claims
- Ensure that employees receive timely medical care under BPJS Kesehatan

8. COMPLIANCE MONITORING AND CUSTOMISATION
{company_name} will conduct regular audits to ensure compliance with all BPJS contribution and enrollment obligations. Each business unit may establish supplementary procedures for BPJS administration, subject to approval by {contact_person}, provided they comply with Law No. 24/2011 and Law No. 40/2004. Monitoring activities include:
- Monthly reconciliation of contribution payments
- Quarterly review of employee enrollment status
- Annual audit of compliance with contribution rates and wage ceilings
- Periodic assessment of claims processing and employee support

9. PENALTIES FOR NON-COMPLIANCE
Failure to comply with BPJS obligations may result in:
- Administrative penalties and fines
- Denial of public services for the company
- Criminal sanctions under Law No. 24/2011

10. CONTACT
For questions about BPJS enrollment, contributions, or claims, contact {hr_contact} or {contact_person}.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
    ],
    "ph": [
        {
            "id": "employment_policy_ph",
            "title": "Employment Policy (Labor Code Compliant)",
            "category": "Core",
            "summary": "Core employment policy aligned with the Philippine Labor Code.",
            "template": """EMPLOYMENT POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
This policy establishes the employment standards and practices of {company_name} in compliance with the Labor Code of the Philippines and related legislation.

2. SECURITY OF TENURE
All regular employees enjoy security of tenure. No employee shall be dismissed except for just or authorised causes and only after due process (twin-notice rule: notice to explain and notice of decision).

3. WORKING HOURS AND OVERTIME
- Normal working hours: 8 hours per day, exclusive of meal breaks.
- Overtime pay: additional 25% of the hourly rate on ordinary days; 30% on rest days, special days, and holidays.
- Night shift differential: additional 10% for work between 10:00 PM and 6:00 AM.

4. WAGES AND BENEFITS
- All employees will be paid at least the applicable regional minimum wage.
- 13th month pay will be provided to all rank-and-file employees no later than December 24 each year.
- Wages will be paid at least twice a month at intervals not exceeding 16 days.
- {company_name} will make required SSS, PhilHealth, and Pag-IBIG contributions.

5. LEAVE ENTITLEMENTS
- Service incentive leave: 5 days per year after 1 year of service.
- Maternity leave: 105 days with pay (RA 11210), with option to extend 30 days without pay.
- Paternity leave: 7 days with pay for married male employees (RA 8187).
- Solo parent leave: 7 days with pay (RA 8972).
- Special leave for women: 2 months for gynaecological surgery (RA 9710).

6. DUE PROCESS IN DISCIPLINARY ACTIONS
{company_name} will follow the twin-notice rule and conduct a fair hearing before imposing any disciplinary action.

7. NON-DISCRIMINATION
{company_name} does not discriminate based on gender, age, disability, religion, ethnicity, or any other protected characteristic.

8. REPORTING CONCERNS
Employees may report concerns to {contact_person} or {hr_contact}, or to the DOLE hotline 1349.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "osh_policy_ph",
            "title": "Occupational Safety & Health Policy (RA 11058)",
            "category": "Safety",
            "summary": "Workplace safety policy compliant with the Philippine OSH Standards Act.",
            "template": """OCCUPATIONAL SAFETY AND HEALTH POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to ensuring the safety and health of all workers in compliance with Republic Act No. 11058 (Occupational Safety and Health Standards Act) and its Implementing Rules and Regulations.

2. EMPLOYER DUTIES
{company_name} will:
- Furnish a workplace free from hazardous conditions
- Provide necessary safety and health training at no cost to workers
- Provide PPE and safety equipment at no cost
- Comply with OSH standards and submit required reports to DOLE
- Designate a qualified Safety Officer and establish a Safety Committee

3. WORKER RIGHTS
Workers have the right to:
- Know about workplace hazards and safety measures
- Refuse unsafe work without threat of retaliation
- Report safety violations to DOLE
- Access OSH training
- Be free from retaliation for exercising OSH rights

4. SAFETY COMMITTEE
A workplace Safety and Health Committee will be established, consisting of employer and worker representatives, to review safety performance and recommend improvements.

5. INCIDENT REPORTING
All work-related accidents, illnesses, and dangerous occurrences must be reported within the timeframes prescribed by DOLE.

6. EMERGENCY PREPAREDNESS
Emergency procedures, including fire evacuation and first aid, are established and communicated to all workers.

7. PENALTIES
Failure to comply with OSH standards may result in fines, work stoppage orders, or criminal liability as provided by RA 11058.

8. CONTACT
For safety concerns, contact {contact_person} or {hr_contact}.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "anti_harassment_ph",
            "title": "Anti-Sexual Harassment & Safe Spaces Policy",
            "category": "Core",
            "summary": "Compliance with RA 7877 (workplace harassment by persons of authority) and RA 11313 (Safe Spaces Act / Bawal Bastos Law), including CODI requirement and penalties.",
            "template": """ANTI-SEXUAL HARASSMENT AND SAFE SPACES POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to providing a workplace free from sexual harassment and gender-based violence. This policy implements the requirements of Republic Act No. 7877 (Anti-Sexual Harassment Act of 1995) and Republic Act No. 11313 (Safe Spaces Act or Bawal Bastos Law).

2. SCOPE
This policy applies to all employees, supervisors, managers, officers, contractors, clients, and visitors of {company_name} in the Philippines. It covers conduct in the workplace, work-related events, online communications, and public spaces in connection with work.

3. SEXUAL HARASSMENT UNDER RA 7877
Sexual harassment in the workplace is committed by a person who has authority, influence, or moral ascendancy over another, when:
a) The sexual favour is made a condition for hiring, employment, re-employment, or continued employment (quid pro quo); or
b) The refusal to grant the sexual favour results in limiting, segregating, or classifying the employee in ways that discriminate or diminish employment opportunities; or
c) The conduct creates an intimidating, hostile, or offensive work environment.

4. GENDER-BASED HARASSMENT UNDER RA 11313 (SAFE SPACES ACT)
The Safe Spaces Act covers gender-based sexual harassment in the workplace, including:
a) Unwelcome sexual advances, requests, or demands for sexual favours
b) Sexist, homophobic, or transphobic slurs, statements, or jokes
c) Use of sexual or discriminatory language
d) Persistent telling of sexual jokes
e) Unwanted sexual comments about a person's body
f) Catcalling, wolf-whistling, or other forms of street-level harassment in connection with work
g) Online gender-based sexual harassment including uploading or sharing of sexual content without consent

5. COMMITTEE ON DECORUM AND INVESTIGATION (CODI)
In compliance with RA 7877 and RA 11313, {company_name} establishes a Committee on Decorum and Investigation (CODI) composed of:
- At least one representative from management
- At least one representative from employees (selected by employees)
- At least one representative from the union (if applicable)
The CODI shall:
- Receive and investigate complaints of sexual harassment
- Create awareness on sexual harassment
- Recommend appropriate disciplinary action
- Ensure due process for both complainant and respondent

6. COMPLAINT PROCEDURE
a) A complaint may be filed with the CODI, {contact_person}, or {hr_contact}.
b) The complaint may be written or verbal and shall detail the incident(s).
c) The CODI shall investigate within 10 days of receiving the complaint.
d) Both parties will be given the opportunity to be heard.
e) The CODI shall submit its findings and recommendations within 30 days.

7. PENALTIES
a) Under RA 7877: Imprisonment of 1-6 months and/or fine of P10,000-P20,000.
b) Under RA 11313: Fines ranging from P1,000 to P500,000 depending on severity, and/or imprisonment.
c) Administrative penalties: Warning, reprimand, suspension, demotion, or termination depending on the gravity of the offence.

8. EMPLOYER DUTIES UNDER RA 11313
{company_name} is required to:
- Disseminate this policy to all employees
- Provide gender sensitivity training and seminars
- Establish the CODI and internal mechanisms for complaint resolution
- Provide safe reporting channels

9. NO RETALIATION
{company_name} strictly prohibits retaliation against any person who files a complaint, participates in an investigation, or serves as a witness. Retaliation is a separate offence subject to disciplinary action.

10. COMPLIANCE CUSTOMISATION
{company_name} departments may establish supplementary procedures for implementing this policy in their specific work environments, subject to CODI oversight and approval by {contact_person}, provided they meet all requirements of RA 7877 and RA 11313.

11. TRAINING
All employees will receive orientation on this policy upon hire and periodic training on sexual harassment prevention and the Safe Spaces Act.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "wages_benefits_ph",
            "title": "Wages & Benefits Policy",
            "category": "Compensation",
            "summary": "Regional minimum wage, 13th month pay (PD 851), holiday pay rates, night shift differential, and SSS/PhilHealth/Pag-IBIG contributions, referencing RA 6727, PD 851, and Labor Code Book III.",
            "template": """WAGES AND BENEFITS POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to fair and lawful compensation of all employees in compliance with the Labor Code of the Philippines (Book III), Republic Act No. 6727 (Wage Rationalisation Act), Presidential Decree No. 851 (13th Month Pay Law), and related wage orders and regulations.

2. SCOPE
This policy applies to all employees of {company_name} in the Philippines, including regular, probationary, seasonal, and project-based employees, unless specifically exempted by law.

3. MINIMUM WAGE (RA 6727)
- All employees will be paid at least the applicable regional daily minimum wage as set by the Regional Tripartite Wages and Productivity Board.
- {company_name} will monitor and implement wage order adjustments within the prescribed period.
- Wages will not be reduced on the basis of any wage order or adjustment.

4. PAYMENT OF WAGES
- Wages will be paid at least twice a month, at intervals not exceeding 16 days.
- Payment will be made in legal tender (Philippine Peso) directly to the employee, or via bank transfer with the employee's written consent.
- No deductions from wages will be made except those authorised by law, collective bargaining agreement, or with the employee's written consent.
- Itemised pay slips will be provided with each payment.

5. 13TH MONTH PAY (PD 851)
- All rank-and-file employees who have worked for at least one month during the calendar year are entitled to 13th month pay.
- 13th month pay is equivalent to one-twelfth (1/12) of the total basic salary earned within the calendar year.
- Payment shall be made no later than December 24 of each year.
- Resigned or separated employees are entitled to a proportionate 13th month pay.

6. OVERTIME PAY
In accordance with the Labor Code:
- Ordinary day overtime: Additional 25% of the hourly rate for work beyond 8 hours.
- Rest day / special non-working day overtime: Additional 30% of the hourly rate.
- Regular holiday overtime: Additional 30% of the applicable holiday rate.
- Double holiday: Rates as prescribed by DOLE.

7. HOLIDAY PAY
a) Regular holidays (Art. 94):
   - Employee who did not work: Entitled to 100% of daily wage.
   - Employee who worked: Entitled to 200% of daily wage.
b) Special non-working days:
   - Employee who did not work: No pay (unless company policy provides otherwise).
   - Employee who worked: Entitled to additional 30% of daily wage.

8. NIGHT SHIFT DIFFERENTIAL
Employees working between 10:00 PM and 6:00 AM are entitled to an additional 10% of their regular wage for each hour of night work, as provided under the Labor Code.

9. MANDATORY CONTRIBUTIONS
{company_name} will ensure timely and accurate remittance of the following statutory contributions:
a) Social Security System (SSS): Employer and employee shares as prescribed by the SSS contribution table.
b) Philippine Health Insurance Corporation (PhilHealth): Employer and employee shares based on monthly basic salary.
c) Home Development Mutual Fund (Pag-IBIG): Employer contribution of P100 and employee contribution of P100 (or 2% of salary, whichever is higher, based on the employee's choice).

10. SERVICE CHARGES
Where applicable, service charges collected by the establishment will be distributed to rank-and-file employees as required by law.

11. COMPLIANCE MONITORING AND CUSTOMISATION
{company_name} will maintain records of all wage and benefit payments for at least 3 years as required by law. Departments may establish supplementary compensation guidelines, subject to approval by {contact_person}, provided they meet or exceed statutory requirements. Monitoring includes:
- Monthly review of minimum wage compliance against current wage orders
- Quarterly audit of statutory contribution remittances
- Annual review of 13th month pay calculations
- Periodic verification of overtime and holiday pay computations

12. EMPLOYEE RIGHTS
- Employees may not waive their right to statutory wages and benefits.
- Employees who believe they have not been properly compensated should contact {hr_contact} or {contact_person}. Complaints may also be filed with the DOLE Regional Office or NLRC.
- No employee will face retaliation for raising compensation concerns.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "security_tenure_ph",
            "title": "Security of Tenure & Due Process Policy",
            "category": "Core",
            "summary": "Twin-notice rule, just causes (Art 297) and authorised causes (Art 298-299), separation pay, constructive dismissal, and NLRC filing under Labor Code Articles 294-299.",
            "template": """SECURITY OF TENURE AND DUE PROCESS POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} recognises and upholds the constitutional right of every employee to security of tenure. This policy ensures that all termination and disciplinary actions comply with the Labor Code of the Philippines (Articles 294-299) and the requirements of substantive and procedural due process.

2. SCOPE
This policy applies to all regular, probationary, and project/seasonal employees of {company_name} in the Philippines.

3. SECURITY OF TENURE (ARTICLE 294)
Every employee who has been engaged to perform activities that are usually necessary or desirable in the usual business of {company_name} shall be considered a regular employee. Regular employees shall not be terminated except for just cause or authorised cause, and only after observance of due process.

4. JUST CAUSES FOR TERMINATION (ARTICLE 297)
An employee may be terminated for any of the following just causes:
a) Serious misconduct or wilful disobedience of lawful orders connected with work
b) Gross and habitual neglect of duties
c) Fraud or wilful breach of trust reposed by the employer
d) Commission of a crime or offence against the employer, their family, or representative
e) Other analogous causes

5. AUTHORISED CAUSES FOR TERMINATION (ARTICLES 298-299)
An employee may be terminated for any of the following authorised causes:
a) Installation of labour-saving devices (Art. 298)
b) Redundancy (Art. 298)
c) Retrenchment to prevent losses (Art. 298)
d) Closure or cessation of business (Art. 298)
e) Disease not curable within 6 months and continued employment is prejudicial (Art. 299)

6. DUE PROCESS — TWIN-NOTICE RULE (JUST CAUSES)
For terminations based on just causes, {company_name} must observe the twin-notice rule:
a) First notice (Notice to Explain / Show-Cause Memo):
   - Written notice specifying the grounds for termination
   - Detailed narration of the facts and circumstances
   - A directive giving the employee a reasonable period (at least 5 calendar days) to submit a written explanation
b) Hearing/Conference:
   - The employee will be given a meaningful opportunity to be heard and present evidence
   - The employee may be assisted by a representative
   - {company_name} will consider the employee's explanation and evidence
c) Second notice (Notice of Decision):
   - Written notice informing the employee of {company_name}'s decision
   - Must clearly state the reasons for the decision
   - If termination, must specify the effective date

7. DUE PROCESS — AUTHORISED CAUSES
For terminations based on authorised causes:
a) Written notice to the employee at least 30 days before the intended date of termination
b) Written notice to DOLE at least 30 days before the intended date of termination
c) Payment of separation pay as prescribed by law

8. SEPARATION PAY
a) For authorised causes under Article 298 (labour-saving devices, redundancy):
   - At least one month pay OR one month pay per year of service, whichever is higher
b) For authorised causes under Articles 298-299 (retrenchment, closure, disease):
   - At least one-half month pay per year of service
c) A fraction of at least 6 months of service is considered one whole year for computation purposes

9. CONSTRUCTIVE DISMISSAL
{company_name} recognises that constructive dismissal — where an employee is forced to resign due to harsh, hostile, or unfavourable conditions created by the employer — is illegal. Actions that constitute constructive dismissal include:
- Demotion without valid cause
- Diminution of pay or benefits without valid cause
- Transfer designed to make the employee's continued employment unreasonable
- Creating a hostile work environment to force resignation

10. PREVENTIVE SUSPENSION
{company_name} may place an employee under preventive suspension only if:
- The employee's continued presence poses a serious and imminent threat to life or property
- Preventive suspension shall not exceed 30 days
- If the case is not resolved within 30 days, the employee must be reinstated or placed on payroll

11. PROBATIONARY EMPLOYMENT
- Probationary employees may be terminated for just cause or for failure to meet reasonable standards made known at the time of engagement.
- The probationary period shall not exceed 6 months from the date of employment.
- Probationary employees who are allowed to work beyond 6 months are deemed regular employees.

12. COMPLIANCE CUSTOMISATION
{company_name} departments may develop supplementary disciplinary procedures and codes of conduct, subject to approval by {contact_person}, provided they comply with the due process requirements of this policy and the Labor Code.

13. FILING WITH NLRC
Employees who believe they have been illegally dismissed may file a complaint with the National Labor Relations Commission (NLRC) within 4 years from the date of termination. Employees may also seek assistance from the DOLE Single Entry Approach (SEnA) for mandatory conciliation-mediation before formal filing.

14. CONTACT
For questions about this policy or employment status, contact {hr_contact} or {contact_person}.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
    ],
    "th": [
        {
            "id": "employment_policy_th",
            "title": "Employment Policy (Labor Protection Act)",
            "category": "Core",
            "summary": "Core employment policy aligned with Thailand's Labor Protection Act.",
            "template": """EMPLOYMENT POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
This policy establishes the employment standards and practices of {company_name} in compliance with the Labor Protection Act B.E. 2541 (1998) and its amendments.

2. WORKING HOURS
- Normal working hours: maximum 8 hours per day and 48 hours per week.
- For hazardous work: maximum 7 hours per day and 42 hours per week.
- Rest period: at least 1 hour after 5 consecutive hours of work.
- At least 1 rest day per week, with not more than 6 consecutive working days.

3. OVERTIME AND HOLIDAY WORK
- Overtime on working days: 1.5x the hourly wage rate.
- Work on holidays: 1x additional pay for employees entitled to holidays; 2x for those not normally entitled.
- Overtime on holidays: 3x the hourly wage rate.
- Overtime requires employee consent except in certain circumstances.

4. WAGES
- All employees will be paid at least the applicable minimum wage rate.
- Wages will be paid at least once a month at the workplace or via bank transfer.
- {company_name} will make required social security contributions.

5. LEAVE ENTITLEMENTS
- Annual leave: at least 6 working days per year after 1 year of service (accumulation permitted).
- Sick leave: up to 30 working days per year with pay (medical certificate required after 3+ days).
- Maternity leave: 98 days (45 days paid by employer, remainder by Social Security).
- Personal business leave: at least 3 days per year with pay.
- Ordination/Hajj leave and military service leave as required by law.

6. SEVERANCE PAY
Employees terminated without cause are entitled to severance pay:
- 120 days to 3 years: 30 days' wages
- 3 to 6 years: 90 days' wages
- 6 to 10 years: 200 days' wages
- 10 to 20 years: 300 days' wages
- 20+ years: 400 days' wages

7. TERMINATION
- Advance notice of at least one pay period, or payment in lieu, is required.
- Employees cannot be dismissed for exercising their legal rights or filing complaints.

8. REPORTING CONCERNS
Employees may report concerns to {contact_person} or {hr_contact}, or to the Labour Protection and Welfare Office.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "safety_policy_th",
            "title": "Occupational Safety & Health Policy",
            "category": "Safety",
            "summary": "Workplace safety policy aligned with Thai OSH legislation.",
            "template": """OCCUPATIONAL SAFETY AND HEALTH POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to ensuring workplace safety and health in compliance with the Occupational Safety, Health and Environment Act B.E. 2554 (2011) and related ministerial regulations.

2. EMPLOYER DUTIES
{company_name} will:
- Provide a safe working environment and maintain safe systems of work
- Appoint a Safety Officer and establish a Safety Committee as required by law
- Provide OSH training and PPE at no cost to employees
- Conduct risk assessments and implement control measures
- Report workplace accidents and occupational diseases as required

3. EMPLOYEE DUTIES
All employees must:
- Comply with safety rules and use PPE provided
- Report hazards, accidents, and unsafe conditions immediately
- Cooperate with the employer on safety matters
- Not remove or disable safety equipment

4. SAFETY COMMITTEE
Establishments with 50 or more employees must have a Safety Committee with employer and employee representatives to oversee OSH matters.

5. INCIDENT REPORTING
Workplace accidents causing death, serious injury, or significant property damage must be reported to the relevant authority within the prescribed timeframe.

6. TRAINING
All employees will receive OSH training appropriate to their roles and workplace hazards.

7. CONTACT
For safety concerns, contact {contact_person} or {hr_contact}.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "anti_harassment_th",
            "title": "Anti-Harassment Policy",
            "category": "Core",
            "summary": "LPA Section 16 (sexual harassment by employers/supervisors), Gender Equality Act B.E. 2558 (gender-based discrimination), complaint mechanisms, and disciplinary action.",
            "template": """ANTI-HARASSMENT POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to providing a workplace free from sexual harassment and gender-based discrimination. This policy is established in compliance with Section 16 of the Labor Protection Act B.E. 2541 (1998) and the Gender Equality Act B.E. 2558 (2015).

2. SCOPE
This policy applies to all employees, supervisors, managers, officers, contractors, and visitors at all {company_name} workplaces and work-related events in Thailand.

3. SEXUAL HARASSMENT UNDER LPA SECTION 16
Section 16 of the Labor Protection Act prohibits an employer, supervisor, or work inspector from committing sexual harassment against an employee. Sexual harassment includes:
- Unwelcome sexual advances or requests for sexual favours
- Unwanted physical contact of a sexual nature
- Sexually suggestive comments, jokes, or gestures
- Display of offensive or pornographic materials in the workplace
- Any other verbal, non-verbal, or physical conduct of a sexual nature that is unwelcome
This prohibition applies whether the victim is male, female, or of any gender identity.

4. GENDER-BASED DISCRIMINATION UNDER GENDER EQUALITY ACT B.E. 2558
The Gender Equality Act prohibits unfair gender discrimination by any person, including employers. Prohibited conduct includes:
- Discrimination in employment on the basis of gender
- Establishing rules, regulations, announcements, or conditions that are discriminatory based on gender
- Treating a person differently on the basis of gender in a way that is an impediment or restriction, unless justified by the nature of the work
- Sexual harassment
Exceptions apply only when justified by the nature of the work or academic purposes, by established religious principles, or for national security.

5. PROHIBITED CONDUCT
{company_name} prohibits the following conduct:
a) Sexual harassment in any form (verbal, physical, visual, or electronic)
b) Requests for sexual favours as a condition of employment, promotion, or favourable treatment
c) Retaliation against any person who reports harassment or cooperates in an investigation
d) Gender-based discrimination in hiring, compensation, promotion, training, or termination
e) Creating a hostile, intimidating, or offensive work environment based on gender

6. COMPLAINT MECHANISM
a) Employees who experience or witness harassment should report to {contact_person} or {hr_contact}.
b) Reports may be made verbally or in writing.
c) Under the Gender Equality Act, employees may also file a complaint with the Committee on the Consideration of Unfair Gender Discrimination.
d) {company_name} will acknowledge receipt of all complaints and commence investigation promptly.

7. INVESTIGATION
- All complaints will be investigated promptly, impartially, and confidentially.
- Both the complainant and the respondent will be given the opportunity to present their account.
- Investigations will be completed within a reasonable timeframe.
- {company_name} will take appropriate interim measures to protect the complainant during the investigation.

8. DISCIPLINARY ACTION
Employees found to have engaged in sexual harassment or gender-based discrimination will face disciplinary action, which may include:
- Written warning
- Suspension without pay
- Demotion
- Termination with cause (no severance pay) under LPA Section 119(1) — serious misconduct
{company_name} notes that under Section 16 of the LPA, if an employer commits sexual harassment, the employee has the right to terminate employment and claim severance pay and compensation.

9. LEGAL REMEDIES
- Under the Gender Equality Act, the Committee on the Consideration of Unfair Gender Discrimination may order remedial measures, compensation, and corrective action.
- Under the LPA, sexual harassment by an employer constitutes grounds for the employee to terminate employment with right to severance pay.
- Criminal remedies may also be available under the Criminal Code.

10. COMPLIANCE CUSTOMISATION
{company_name} departments may establish supplementary anti-harassment procedures tailored to their work environment, subject to approval by {contact_person}, provided they meet the requirements of this policy, the LPA, and the Gender Equality Act.

11. TRAINING
All employees will receive anti-harassment training upon hire and periodically thereafter. Supervisors and managers will receive additional training on their obligations under this policy and applicable law.

12. NO RETALIATION
{company_name} strictly prohibits retaliation against any person who reports harassment, files a complaint, or participates in an investigation. Retaliation is a separate disciplinary offence.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
        {
            "id": "social_security_th",
            "title": "Social Security Compliance Policy",
            "category": "Compliance",
            "summary": "Social Security Act B.E. 2533 compliance covering employer/employee 5% contributions and 7 benefit categories (sickness, maternity, invalidity, death, child, old-age, unemployment).",
            "template": """SOCIAL SECURITY COMPLIANCE POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to fulfilling its social security obligations under the Social Security Act B.E. 2533 (1990) and its amendments. This policy establishes procedures for enrollment, contributions, and benefit administration for all employees in Thailand.

2. SCOPE
This policy applies to all employees of {company_name} in Thailand. Under the Social Security Act, employers with one or more employees are required to register with the Social Security Office (SSO) and make contributions.

3. REGISTRATION AND ENROLLMENT
- {company_name} will register with the Social Security Office within 30 days of hiring the first employee.
- All new employees will be enrolled with the SSO within 30 days of commencing employment.
- {company_name} will ensure that each employee receives their social security card and number.
- Changes in employee information will be reported to the SSO within the prescribed timeframe.

4. CONTRIBUTION RATES
- Employer contribution: 5% of monthly wages (subject to a wage ceiling as prescribed by the SSO).
- Employee contribution: 5% of monthly wages (subject to the same wage ceiling).
- Government contribution: As prescribed by law for each benefit category.
- The wage ceiling for contribution calculation is as determined by ministerial regulation (currently THB 15,000 per month, subject to change).
- {company_name} will deduct the employee's share from monthly wages and remit both the employer and employee contributions to the SSO by the 15th of the following month.

5. SEVEN BENEFIT CATEGORIES
Contributions fund the following 7 benefit categories:

a) Sickness Benefit (Section 62-64)
   - Cash benefit of 50% of wages for up to 90 days per time (maximum 180 days per year) when an employee is unable to work due to non-work-related illness.
   - Medical treatment at the employee's registered hospital under the SSO network.
   - Dental care benefits as prescribed.

b) Maternity Benefit (Section 65-67)
   - Cash benefit of 50% of wages for 90 days per pregnancy.
   - Reimbursement of delivery expenses for up to 2 pregnancies.
   - Prenatal care and postnatal check-up coverage.

c) Invalidity Benefit (Section 68-74)
   - Cash benefit of 50% of wages for employees who become disabled due to non-work-related causes.
   - Medical treatment and rehabilitation services.
   - Benefits continue for as long as the disability persists.

d) Death Benefit (Section 73-76)
   - Funeral grant to the person who arranges the funeral.
   - Lump-sum payment to the designated beneficiary or legal heirs.
   - Eligibility requires a minimum contribution period.

e) Child Allowance (Section 74-76)
   - Monthly allowance per child (up to 3 children at a time) from birth until the child reaches 6 years of age.
   - Applicable to legitimate children, adopted children, or children acknowledged by the insured.

f) Old-Age Benefit (Section 76-77)
   - Lump-sum payment if contributions were made for less than 180 months.
   - Monthly pension if contributions were made for 180 months or more.
   - Payable from age 55 when the insured ceases employment.
   - Additional pension supplement for contributions exceeding 180 months.

g) Unemployment Benefit (Section 78-80)
   - Involuntary unemployment: Cash benefit of 50% of wages for up to 180 days per year.
   - Voluntary resignation: Cash benefit of 30% of wages for up to 90 days per year.
   - Requires a minimum contribution period of 6 months within the preceding 15 months.
   - Employees must register at the employment office and be available for suitable work.

6. EMPLOYEE ENTITLEMENTS
- Employees are entitled to choose one hospital from the SSO network as their designated hospital for medical treatment.
- {company_name} will facilitate hospital selection and changes as needed.
- Employees may access benefits by presenting their social security card at their registered hospital.

7. CLAIMS AND DOCUMENTATION
{company_name} will:
- Assist employees in understanding their social security entitlements
- Provide necessary documentation for benefit claims (e.g., salary certificates, employment records)
- Support employees in the claims process for sickness, maternity, invalidity, and other benefits
- Maintain records required by the SSO

8. COMPLIANCE MONITORING AND CUSTOMISATION
{company_name} will conduct regular reviews to ensure compliance with Social Security Act obligations. Each business unit may establish supplementary procedures for social security administration, subject to approval by {contact_person}, provided they comply with the Social Security Act B.E. 2533 and related regulations. Monitoring includes:
- Monthly reconciliation of contribution payments
- Quarterly review of employee enrollment status
- Annual audit of contribution calculations against current wage ceilings
- Periodic review of hospital registration and employee entitlements

9. PENALTIES FOR NON-COMPLIANCE
Failure to comply with social security obligations may result in:
- Surcharges of 2% per month on late contributions
- Fines for failure to register, failure to submit forms, or providing false information
- Criminal penalties for deliberate non-compliance

10. CONTACT
For questions about social security enrollment, contributions, or benefits, contact {hr_contact} or {contact_person}.

Approved by: ____________________
Title: ____________________
Date: {effective_date}""",
        },
    ],
}


def _get_all_templates_for_country(country_code: str) -> list[dict]:
    """Return policy templates for the given country."""
    return POLICY_TEMPLATES_BY_COUNTRY.get(country_code, POLICY_TEMPLATES_BY_COUNTRY["us"])


@router.get("/", response_class=HTMLResponse)
async def policies_list(
    request: Request,
    country: str | None = None,
    user: User = Depends(get_current_user),
):
    if country and country in POLICY_TEMPLATES_BY_COUNTRY:
        selected = country
    else:
        selected = user.country

    policy_templates = _get_all_templates_for_country(selected)
    return templates.TemplateResponse(
        "policies.html",
        {
            "request": request,
            "user": user,
            "policies": policy_templates,
            "countries": COUNTRY_NAMES,
            "selected_country": selected,
        },
    )


@router.get("/custom", response_class=HTMLResponse)
async def custom_policy_form(request: Request, user: User = Depends(get_current_user)):
    if not user.is_subscribed:
        return RedirectResponse("/subscribe?next=/policies/custom", status_code=303)
    return templates.TemplateResponse(
        "policy_custom_form.html",
        {"request": request, "user": user, "countries": COUNTRY_NAMES},
    )


@router.post("/custom/generate", response_class=HTMLResponse)
async def generate_custom_policy(
    request: Request,
    topic: str = Form(...),
    company_name: str = Form(...),
    country: str = Form("us"),
    effective_date: str = Form(""),
    contact_person: str = Form(""),
    additional_requirements: str = Form(""),
    user: User = Depends(get_current_user),
):
    if not user.is_subscribed:
        return RedirectResponse("/subscribe?next=/policies/custom", status_code=303)

    country_name = COUNTRY_NAMES.get(country, "United States")
    company = company_name or "[Company Name]"
    date = effective_date or "[Date]"
    contact = contact_person or "[Contact Person]"

    additional_section = ""
    if additional_requirements.strip():
        additional_section = f"""
ADDITIONAL PROVISIONS
{additional_requirements.strip()}
"""

    rendered = f"""{topic.upper()} POLICY

Company: {company}
Country/Region: {country_name}
Effective Date: {date}

1. PURPOSE
{company} establishes this {topic} policy to provide clear guidelines and standards for all employees. This policy is designed to comply with applicable employment laws in {country_name}.

2. SCOPE
This policy applies to all employees, contractors, and agents of {company} operating in {country_name}.

3. POLICY STATEMENT
{company} is committed to implementing and maintaining standards for {topic.lower()} that promote a fair, safe, and productive work environment. All employees are expected to comply with the guidelines set forth in this policy.

4. GUIDELINES AND STANDARDS
a) {company} will establish and communicate clear standards regarding {topic.lower()}.
b) All employees must familiarise themselves with and adhere to these standards.
c) Managers and supervisors are responsible for ensuring compliance within their teams.
d) Regular reviews will be conducted to ensure the policy remains current and effective.

5. ROLES AND RESPONSIBILITIES
Management:
- Ensure the policy is communicated to all employees
- Provide necessary resources and training
- Monitor compliance and address non-compliance promptly

Employees:
- Read, understand, and comply with this policy
- Report concerns or violations to {contact}
- Participate in relevant training programmes

6. COMPLIANCE AND ENFORCEMENT
Violations of this policy may result in disciplinary action, up to and including termination of employment. {company} will investigate all reported violations promptly and impartially.

7. LEGAL FRAMEWORK
This policy is designed to align with the employment laws and regulations of {country_name}. Where local law provides greater protections, those provisions will apply.

8. REPORTING AND GRIEVANCES
Employees who have concerns about this policy or wish to report a violation should contact {contact}. All reports will be treated confidentially and investigated promptly.

9. REVIEW
This policy will be reviewed annually and updated as needed to reflect changes in law, best practices, or organisational needs.
{additional_section}
Approved by: ____________________
Title: ____________________
Date: {date}

DISCLAIMER: This policy provides a general framework and should be reviewed by legal counsel to ensure full compliance with the specific laws and regulations of {country_name} applicable to your organisation."""

    return templates.TemplateResponse(
        "policy_custom_result.html",
        {
            "request": request,
            "user": user,
            "topic": topic,
            "rendered": rendered,
            "company_name": company,
        },
    )


@router.get("/{policy_id}", response_class=HTMLResponse)
async def policy_form(
    policy_id: str,
    request: Request,
    country: str | None = None,
    user: User = Depends(get_current_user),
):
    if not user.is_subscribed:
        return RedirectResponse("/subscribe?next=/policies/" + policy_id, status_code=303)

    if country and country in POLICY_TEMPLATES_BY_COUNTRY:
        selected = country
    else:
        selected = user.country

    policy_templates = _get_all_templates_for_country(selected)
    policy = next((p for p in policy_templates if p["id"] == policy_id), None)
    if not policy:
        return RedirectResponse("/policies", status_code=303)
    return templates.TemplateResponse(
        "policy_form.html",
        {"request": request, "user": user, "policy": policy, "selected_country": selected},
    )


@router.post("/{policy_id}/generate", response_class=HTMLResponse)
async def generate_policy(
    policy_id: str,
    request: Request,
    company_name: str = Form(...),
    effective_date: str = Form(""),
    contact_person: str = Form(""),
    hr_contact: str = Form(""),
    country: str = Form("us"),
    user: User = Depends(get_current_user),
):
    if not user.is_subscribed:
        return RedirectResponse("/subscribe?next=/policies/" + policy_id, status_code=303)

    if country and country in POLICY_TEMPLATES_BY_COUNTRY:
        selected = country
    else:
        selected = user.country

    policy_templates = _get_all_templates_for_country(selected)
    policy = next((p for p in policy_templates if p["id"] == policy_id), None)
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
            "selected_country": selected,
        },
    )

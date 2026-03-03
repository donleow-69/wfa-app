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
            "title": "TAFEP-Compliant Fair Employment Policy",
            "category": "Core",
            "summary": "Ensures non-discriminatory hiring and employment practices per TAFEP guidelines.",
            "template": """FAIR EMPLOYMENT POLICY

Company: {company_name}
Effective Date: {effective_date}

1. PURPOSE
{company_name} is committed to fair and merit-based employment practices in accordance with the Tripartite Guidelines on Fair Employment Practices (TGFEP) and Singapore's workplace fairness legislation.

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
This policy is aligned with the Tripartite Guidelines on Fair Employment Practices and the Employment Act (Cap. 91). Violations will result in disciplinary action.

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

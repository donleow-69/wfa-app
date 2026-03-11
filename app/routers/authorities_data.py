"""Authority lookup data — maps (country, category) to the relevant government authority."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Authority:
    name: str
    email: str
    portal_url: str
    description: str


# AUTHORITIES[country][category] → Authority
AUTHORITIES: dict[str, dict[str, Authority]] = {
    "us": {
        "discrimination": Authority(
            name="Equal Employment Opportunity Commission (EEOC)",
            email="info@eeoc.gov",
            portal_url="https://publicportal.eeoc.gov/Portal/Login.aspx",
            description="Federal agency enforcing workplace anti-discrimination laws.",
        ),
        "retaliation": Authority(
            name="Equal Employment Opportunity Commission (EEOC)",
            email="info@eeoc.gov",
            portal_url="https://publicportal.eeoc.gov/Portal/Login.aspx",
            description="Federal agency handling retaliation and whistleblower complaints.",
        ),
        "harassment": Authority(
            name="Equal Employment Opportunity Commission (EEOC)",
            email="info@eeoc.gov",
            portal_url="https://publicportal.eeoc.gov/Portal/Login.aspx",
            description="Federal agency handling workplace harassment complaints.",
        ),
        "wage_theft": Authority(
            name="Department of Labor — Wage and Hour Division (WHD)",
            email="",
            portal_url="https://www.dol.gov/agencies/whd/contact/complaints",
            description="Enforces federal minimum wage, overtime, and other wage laws.",
        ),
        "leave": Authority(
            name="Department of Labor — Wage and Hour Division (WHD)",
            email="",
            portal_url="https://www.dol.gov/agencies/whd/contact/complaints",
            description="Enforces FMLA and other leave/accommodation protections.",
        ),
        "safety": Authority(
            name="Occupational Safety and Health Administration (OSHA)",
            email="",
            portal_url="https://www.osha.gov/workers/file-complaint",
            description="Enforces workplace safety and health standards.",
        ),
        "other": Authority(
            name="Department of Labor (DOL)",
            email="",
            portal_url="https://www.dol.gov/general/contact",
            description="Federal department overseeing labor standards and worker protections.",
        ),
    },
    "sg": {
        "discrimination": Authority(
            name="Tripartite Alliance for Fair & Progressive Employment Practices (TAFEP)",
            email="",
            portal_url="https://www.tal.sg/tafep/getting-help/report-employment-issues",
            description="Promotes fair employment practices in Singapore.",
        ),
        "retaliation": Authority(
            name="Ministry of Manpower (MOM)",
            email="mom_fmmd@mom.gov.sg",
            portal_url="https://www.mom.gov.sg/employment-practices/how-to-file-a-claim",
            description="Government ministry overseeing labor and employment matters.",
        ),
        "harassment": Authority(
            name="Ministry of Manpower (MOM)",
            email="mom_fmmd@mom.gov.sg",
            portal_url="https://www.mom.gov.sg/employment-practices/how-to-file-a-claim",
            description="Government ministry overseeing labor and employment matters.",
        ),
        "wage_theft": Authority(
            name="Ministry of Manpower (MOM)",
            email="mom_fmmd@mom.gov.sg",
            portal_url="https://www.mom.gov.sg/employment-practices/how-to-file-a-claim",
            description="Government ministry overseeing labor and employment matters.",
        ),
        "leave": Authority(
            name="Ministry of Manpower (MOM)",
            email="mom_fmmd@mom.gov.sg",
            portal_url="https://www.mom.gov.sg/employment-practices/how-to-file-a-claim",
            description="Government ministry overseeing labor and employment matters.",
        ),
        "safety": Authority(
            name="Ministry of Manpower — OSHD",
            email="mom_oshd@mom.gov.sg",
            portal_url="https://www.mom.gov.sg/workplace-safety-and-health/report",
            description="Occupational Safety and Health Division under MOM.",
        ),
        "other": Authority(
            name="Ministry of Manpower (MOM)",
            email="mom_fmmd@mom.gov.sg",
            portal_url="https://www.mom.gov.sg/employment-practices/how-to-file-a-claim",
            description="Government ministry overseeing labor and employment matters.",
        ),
    },
    "my": {
        "discrimination": Authority(
            name="Jabatan Tenaga Kerja Semenanjung Malaysia (JTKSM)",
            email="jtksm@mohr.gov.my",
            portal_url="https://jtksm.mohr.gov.my/en/complaint",
            description="Department of Labour handling employment complaints.",
        ),
        "retaliation": Authority(
            name="Industrial Court of Malaysia",
            email="mp@mp.gov.my",
            portal_url="https://www.mp.gov.my/en/",
            description="Handles unfair dismissal and retaliation claims.",
        ),
        "harassment": Authority(
            name="Tribunal Anti-Gangguan Seksual",
            email="",
            portal_url="https://www.mohr.gov.my/en/",
            description="Anti-Sexual Harassment Tribunal under the Ministry of Human Resources.",
        ),
        "wage_theft": Authority(
            name="Jabatan Tenaga Kerja Semenanjung Malaysia (JTKSM)",
            email="jtksm@mohr.gov.my",
            portal_url="https://jtksm.mohr.gov.my/en/complaint",
            description="Department of Labour handling wage and employment complaints.",
        ),
        "leave": Authority(
            name="Jabatan Tenaga Kerja Semenanjung Malaysia (JTKSM)",
            email="jtksm@mohr.gov.my",
            portal_url="https://jtksm.mohr.gov.my/en/complaint",
            description="Department of Labour handling leave and employment complaints.",
        ),
        "safety": Authority(
            name="Department of Occupational Safety and Health (DOSH)",
            email="jkkp@mohr.gov.my",
            portal_url="https://www.dosh.gov.my/index.php/en/complaint",
            description="Government department overseeing workplace safety standards.",
        ),
        "other": Authority(
            name="Jabatan Tenaga Kerja Semenanjung Malaysia (JTKSM)",
            email="jtksm@mohr.gov.my",
            portal_url="https://jtksm.mohr.gov.my/en/complaint",
            description="Department of Labour handling employment complaints.",
        ),
    },
    "id": {
        "discrimination": Authority(
            name="Kementerian Ketenagakerjaan (Kemnaker)",
            email="",
            portal_url="https://kemnaker.go.id/",
            description="Ministry of Manpower of the Republic of Indonesia.",
        ),
        "retaliation": Authority(
            name="Kementerian Ketenagakerjaan (Kemnaker)",
            email="",
            portal_url="https://kemnaker.go.id/",
            description="Ministry of Manpower of the Republic of Indonesia.",
        ),
        "harassment": Authority(
            name="Kementerian Ketenagakerjaan (Kemnaker)",
            email="",
            portal_url="https://kemnaker.go.id/",
            description="Ministry of Manpower of the Republic of Indonesia.",
        ),
        "wage_theft": Authority(
            name="Kementerian Ketenagakerjaan (Kemnaker)",
            email="",
            portal_url="https://kemnaker.go.id/",
            description="Ministry of Manpower of the Republic of Indonesia.",
        ),
        "leave": Authority(
            name="Kementerian Ketenagakerjaan (Kemnaker)",
            email="",
            portal_url="https://kemnaker.go.id/",
            description="Ministry of Manpower of the Republic of Indonesia.",
        ),
        "safety": Authority(
            name="Kementerian Ketenagakerjaan (Kemnaker)",
            email="",
            portal_url="https://kemnaker.go.id/",
            description="Ministry of Manpower of the Republic of Indonesia.",
        ),
        "other": Authority(
            name="Kementerian Ketenagakerjaan (Kemnaker)",
            email="",
            portal_url="https://kemnaker.go.id/",
            description="Ministry of Manpower of the Republic of Indonesia.",
        ),
    },
    "ph": {
        "discrimination": Authority(
            name="Department of Labor and Employment (DOLE)",
            email="",
            portal_url="https://www.dole.gov.ph/contact-us/",
            description="Government department overseeing labor and employment.",
        ),
        "retaliation": Authority(
            name="National Labor Relations Commission (NLRC)",
            email="",
            portal_url="https://nlrc.dole.gov.ph/",
            description="Quasi-judicial body handling labor disputes and unfair labor practices.",
        ),
        "harassment": Authority(
            name="Department of Labor and Employment (DOLE)",
            email="",
            portal_url="https://www.dole.gov.ph/contact-us/",
            description="Government department overseeing labor and employment.",
        ),
        "wage_theft": Authority(
            name="Department of Labor and Employment (DOLE)",
            email="",
            portal_url="https://www.dole.gov.ph/contact-us/",
            description="Government department overseeing labor and employment.",
        ),
        "leave": Authority(
            name="Department of Labor and Employment (DOLE)",
            email="",
            portal_url="https://www.dole.gov.ph/contact-us/",
            description="Government department overseeing labor and employment.",
        ),
        "safety": Authority(
            name="Department of Labor and Employment (DOLE)",
            email="",
            portal_url="https://www.dole.gov.ph/contact-us/",
            description="Government department overseeing labor and employment.",
        ),
        "other": Authority(
            name="Department of Labor and Employment (DOLE)",
            email="",
            portal_url="https://www.dole.gov.ph/contact-us/",
            description="Government department overseeing labor and employment.",
        ),
    },
    "gb": {
        "discrimination": Authority(
            name="Equality and Human Rights Commission (EHRC)",
            email="0808 800 0082",
            portal_url="https://www.equalityhumanrights.com",
            description="Enforces the Equality Act 2010 and promotes equality across the nine protected characteristics. Address: Arndale House, The Arndale Centre, Manchester, M4 3AQ",
        ),
        "wages": Authority(
            name="Fair Work Agency / HMRC National Minimum Wage",
            email="0300 123 1100 (ACAS)",
            portal_url="https://www.gov.uk/national-minimum-wage",
            description="Enforces minimum wage compliance and investigates underpayment. The Fair Work Agency consolidates NMW enforcement from April 2026. Address: ACAS, Euston Tower, 286 Euston Road, London, NW1 3JJ",
        ),
        "safety": Authority(
            name="Health and Safety Executive (HSE)",
            email="0300 003 1747",
            portal_url="https://www.hse.gov.uk",
            description="Regulates workplace health and safety under the Health and Safety at Work Act 1974. Address: Redgrave Court, Merton Road, Bootle, Merseyside, L20 7HS",
        ),
        "leave": Authority(
            name="Advisory, Conciliation and Arbitration Service (ACAS)",
            email="0300 123 1100",
            portal_url="https://www.acas.org.uk",
            description="Provides advice on employment rights including leave entitlements, and mandatory pre-claim conciliation. Address: Euston Tower, 286 Euston Road, London, NW1 3JJ",
        ),
        "unfair_dismissal": Authority(
            name="Employment Tribunals (via ACAS)",
            email="0300 123 1100 (ACAS) / 0300 123 1024 (Tribunals)",
            portal_url="https://www.gov.uk/courts-tribunals/employment-tribunal",
            description="Handles unfair dismissal claims. Pre-claim conciliation through ACAS is mandatory before tribunal proceedings. Address: Employment Tribunals (multiple locations across England, Wales, and Scotland)",
        ),
        "harassment": Authority(
            name="Equality and Human Rights Commission (EHRC)",
            email="0808 800 0082",
            portal_url="https://www.equalityhumanrights.com",
            description="Oversees enforcement of harassment protections under the Equality Act 2010 and ERA 2025 preventive duty. Address: Arndale House, The Arndale Centre, Manchester, M4 3AQ",
        ),
        "industrial_relations_gb": Authority(
            name="Central Arbitration Committee (CAC)",
            email="0330 109 3610",
            portal_url="https://www.gov.uk/government/organisations/central-arbitration-committee",
            description="Handles trade union recognition disputes, disclosure of information complaints, and European works council issues. Address: Fleetbank House, 2-6 Salisbury Square, London, EC4Y 8JX",
        ),
    },
    "hk": {
        "discrimination_hk": Authority(
            name="Equal Opportunities Commission (EOC)",
            email="(852) 2511 8211",
            portal_url="https://www.eoc.org.hk",
            description="Investigates discrimination complaints, promotes equal opportunities, and enforces the four discrimination ordinances. Address: 19/F, CityPlaza Three, 14 Taikoo Wan Road, Taikoo Shing, Hong Kong",
        ),
        "wages_hk": Authority(
            name="Labour Department",
            email="(852) 2717 1771",
            portal_url="https://www.labour.gov.hk",
            description="Enforces the Employment Ordinance and Minimum Wage Ordinance, handles wage disputes and employment claims. Address: Harbour Building, 38 Pier Road, Central, Hong Kong",
        ),
        "safety_hk": Authority(
            name="Labour Department, Occupational Safety and Health Branch",
            email="(852) 2559 2297",
            portal_url="https://www.labour.gov.hk",
            description="Inspects workplaces, investigates accidents, and enforces the Occupational Safety and Health Ordinance. Address: Harbour Building, 38 Pier Road, Central, Hong Kong",
        ),
        "leave_hk": Authority(
            name="Labour Department",
            email="(852) 2717 1771",
            portal_url="https://www.labour.gov.hk",
            description="Advises on statutory leave entitlements under the Employment Ordinance and handles related disputes. Address: Harbour Building, 38 Pier Road, Central, Hong Kong",
        ),
        "unfair_dismissal_hk": Authority(
            name="Labour Department / Labour Tribunal",
            email="(852) 2717 1771 (Labour Dept) / (852) 2625 0555 (Tribunal)",
            portal_url="https://www.labour.gov.hk",
            description="Handles employment claims including unreasonable and unlawful dismissal. The Labour Tribunal provides quick and inexpensive dispute resolution. Address: Harbour Building, 38 Pier Road, Central, Hong Kong",
        ),
        "harassment_hk": Authority(
            name="Equal Opportunities Commission (EOC)",
            email="(852) 2511 8211",
            portal_url="https://www.eoc.org.hk",
            description="Handles sexual harassment, disability harassment, and racial harassment complaints under the discrimination ordinances. Address: 19/F, CityPlaza Three, 14 Taikoo Wan Road, Taikoo Shing, Hong Kong",
        ),
        "social_security_hk": Authority(
            name="Mandatory Provident Fund Schemes Authority (MPFA)",
            email="(852) 2918 0102",
            portal_url="https://www.mpfa.org.hk",
            description="Regulates and supervises the MPF system, ensures employer and employee compliance with contribution requirements. Address: Units 2501-08, Level 25, Tower 1, Kowloon Commerce Centre, 51 Kwai Cheong Road, Kwai Chung",
        ),
    },
    "th": {
        "discrimination": Authority(
            name="Department of Labour Protection and Welfare (DLPW)",
            email="",
            portal_url="https://www.labour.go.th/",
            description="Government department handling labour protection in Thailand.",
        ),
        "retaliation": Authority(
            name="Department of Labour Protection and Welfare (DLPW)",
            email="",
            portal_url="https://www.labour.go.th/",
            description="Government department handling labour protection in Thailand.",
        ),
        "harassment": Authority(
            name="Department of Labour Protection and Welfare (DLPW)",
            email="",
            portal_url="https://www.labour.go.th/",
            description="Government department handling labour protection in Thailand.",
        ),
        "wage_theft": Authority(
            name="Department of Labour Protection and Welfare (DLPW)",
            email="",
            portal_url="https://www.labour.go.th/",
            description="Government department handling labour protection in Thailand.",
        ),
        "leave": Authority(
            name="Social Security Office (SSO)",
            email="",
            portal_url="https://www.sso.go.th/",
            description="Government agency handling social security and leave benefits.",
        ),
        "safety": Authority(
            name="Department of Labour Protection and Welfare (DLPW)",
            email="",
            portal_url="https://www.labour.go.th/",
            description="Government department handling labour protection in Thailand.",
        ),
        "other": Authority(
            name="Department of Labour Protection and Welfare (DLPW)",
            email="",
            portal_url="https://www.labour.go.th/",
            description="Government department handling labour protection in Thailand.",
        ),
    },
}

# Fallback authority when country or category is not in the lookup.
_FALLBACK = Authority(
    name="Local Labour Authority",
    email="",
    portal_url="",
    description="Contact your local labour department for assistance.",
)


def get_authority(country: str, category: str) -> Authority:
    """Return the relevant authority for a country/category pair."""
    country_map = AUTHORITIES.get(country, {})
    return country_map.get(category, _FALLBACK)

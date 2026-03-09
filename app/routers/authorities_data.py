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

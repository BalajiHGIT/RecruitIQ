"""Company model."""
from dataclasses import dataclass

@dataclass
class Company:
    company_name: str
    contact_person: str = ""
    email: str = ""
    mobile: str = ""
    location: str = ""

"""Candidate model."""
from dataclasses import dataclass

@dataclass
class Candidate:
    full_name: str
    email: str
    mobile: str
    qualification: str = ""
    percentage: float = 0.0
    passing_year: int | None = None
    technology: str = ""
    skills: str = ""
    backlogs: int = 0

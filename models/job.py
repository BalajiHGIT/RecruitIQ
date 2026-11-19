"""Job model."""
from dataclasses import dataclass


@dataclass
class Job:
    company_id: int
    job_title: str
    openings: int

    qualification_required: str = ""
    minimum_percentage: float = 0.0
    passing_year: int | None = None
    technology: str = ""
    required_skills: str = ""
    max_backlogs: int = 0

    min_package: float | None = None
    max_package: float | None = None
    posted_date: str | None = None
    deadline: str | None = None
    job_status: str = "Open"

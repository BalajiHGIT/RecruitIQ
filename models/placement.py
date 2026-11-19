"""Placement model."""
from dataclasses import dataclass


@dataclass
class Placement:
    candidate_id: int
    company_id: int
    job_id: int
    package: float = 0.0
    placement_status: str = "Confirmed"
    joining_date: str | None = None

"""Interview model."""
from dataclasses import dataclass


@dataclass
class Interview:
    application_id: int
    round_name: str
    interview_date: str
    interviewer: str = ""
    feedback: str = ""
    result: str = "Pending"
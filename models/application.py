"""Job application model."""
from dataclasses import dataclass

@dataclass
class Application:
    candidate_id: int
    job_id: int
    application_status: str = "Applied"

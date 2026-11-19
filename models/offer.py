"""Offer model."""
from dataclasses import dataclass


@dataclass
class Offer:
    application_id: int
    offer_date: str | None = None
    package: float = 0.0
    offer_status: str = "Pending"
    joining_date: str | None = None
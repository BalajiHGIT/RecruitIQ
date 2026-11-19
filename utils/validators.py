"""Input validation helpers."""
import re

def validate_email(email: str) -> bool:
    return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email.strip()))

def validate_mobile(mobile: str) -> bool:
    return bool(re.fullmatch(r"\d{10}", mobile.strip()))

def validate_percentage(value: float) -> bool:
    return 0 <= value <= 100

def validate_openings(value: int) -> bool:
    return value > 0

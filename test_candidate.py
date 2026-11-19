from datetime import datetime

from models.candidate import Candidate
from services.candidate_service import (
    add_candidate,
    get_candidate,
    update_candidate,
    delete_candidate
)

candidate_id = None

try:
    email = f"test{datetime.now():%Y%m%d%H%M%S%f}@example.com"

    candidate = Candidate(
        full_name="Test Candidate",
        email=email,
        mobile="9876543210",
        qualification="BCA",
        percentage=78.50,
        passing_year=2026,
        technology="Python",
        skills="Python, SQL, Django",
        backlogs=0
    )

    candidate_id = add_candidate(candidate)
    print("1. Candidate Added Successfully!")

    data = get_candidate(candidate_id)
    print("2. Candidate Details:", data)

    updated_candidate = Candidate(
        full_name="Test Candidate Updated",
        email=email,
        mobile="9876543210",
        qualification="BCA",
        percentage=80.00,
        passing_year=2026,
        technology="Python",
        skills="Python, SQL, Django",
        backlogs=0
    )

    update_candidate(candidate_id, updated_candidate)
    print("3. Candidate Updated Successfully!")

    delete_candidate(candidate_id)
    candidate_id = None
    print("4. Candidate Deleted Successfully!")

except Exception as error:
    print("Testing Error:", error)

    if candidate_id is not None:
        try:
            delete_candidate(candidate_id)
        except Exception:
            pass
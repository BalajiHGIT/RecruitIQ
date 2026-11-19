
from datetime import date, timedelta
from services.eligibility_service import check_eligibility

# Eligible Candidate
candidate = {
    "full_name": "Balaji Hajare",
    "qualification": "BCA",
    "percentage": 80,
    "passing_year": 2026,
    "technology": "Python",
    "skills": "Python, Django, MySQL, SQL",
    "backlogs": 0,
    "candidate_status": "Active"
}

# Job Requirements
job = {
    "job_title": "Python Developer",
    "qualification_required": "BCA",
    "minimum_percentage": 60,
    "passing_year": 2026,
    "technology": "Python",
    "required_skills": "Python, Django, MySQL",
    "max_backlogs": 0,
    "openings": 3,
    "job_status": "Open",
    "deadline": (date.today() + timedelta(days=30)).isoformat()
}

print("=" * 50)
print(" RECRUITMENT ELIGIBILITY ENGINE")
print("=" * 50)

# Test 1: Eligible Candidate
print("\nTEST 1: Eligible Candidate")

is_eligible, reasons = check_eligibility(candidate, job)

print("Candidate:", candidate["full_name"])
print("Eligibility:", "ELIGIBLE" if is_eligible else "NOT ELIGIBLE")

if reasons:
    for reason in reasons:
        print("-", reason)

assert is_eligible, "Eligible candidate test failed!"

# Test 2: Low Percentage
print("\nTEST 2: Low Percentage")

candidate2 = candidate.copy()
candidate2["percentage"] = 45

is_eligible, reasons = check_eligibility(candidate2, job)

print("Eligibility:", "ELIGIBLE" if is_eligible else "NOT ELIGIBLE")
print("Reason:", reasons)

assert not is_eligible

# Test 3: Missing Skills
print("\nTEST 3: Missing Skills")

candidate3 = candidate.copy()
candidate3["skills"] = "Python"

is_eligible, reasons = check_eligibility(candidate3, job)

print("Eligibility:", "ELIGIBLE" if is_eligible else "NOT ELIGIBLE")
print("Reason:", reasons)

assert not is_eligible

# Test 4: Job Closed
print("\nTEST 4: Job Closed")

closed_job = job.copy()
closed_job["job_status"] = "Closed"

is_eligible, reasons = check_eligibility(candidate, closed_job)

print("Eligibility:", "ELIGIBLE" if is_eligible else "NOT ELIGIBLE")
print("Reason:", reasons)

assert not is_eligible

print("\n" + "=" * 50)
print("ALL 4 ELIGIBILITY TESTS PASSED!")
print("=" * 50)

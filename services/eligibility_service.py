
"""Smart candidate eligibility engine."""

from datetime import date, datetime


def normalize(value):
    return " ".join(str(value or "").strip().lower().split())


def parse_date(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    return date.fromisoformat(str(value))


def check_eligibility(candidate: dict, job: dict) -> tuple[bool, list[str]]:
    reasons = []

    # 1. Candidate status
    if candidate.get("candidate_status", "Active") != "Active":
        reasons.append("Candidate is not active.")

    # 2. Job status
    if job.get("job_status", "Open") != "Open":
        reasons.append("Job is not open.")

    # 3. Job openings
    if int(job.get("openings") or 0) <= 0:
        reasons.append("No job openings are available.")

    # 4. Qualification
    required_qualification = normalize(
        job.get("qualification_required")
    )
    candidate_qualification = normalize(
        candidate.get("qualification")
    )

    if (
        required_qualification
        and candidate_qualification != required_qualification
    ):
        reasons.append("Candidate qualification does not match.")

    # 5. Percentage
    candidate_percentage = float(candidate.get("percentage") or 0)
    minimum_percentage = float(job.get("minimum_percentage") or 0)

    if candidate_percentage < minimum_percentage:
        reasons.append("Candidate percentage is below the job requirement.")

    # 6. Passing Year
    required_year = job.get("passing_year")
    candidate_year = candidate.get("passing_year")

    if required_year is not None and candidate_year is not None:
        if int(candidate_year) != int(required_year):
            reasons.append("Candidate passing year does not match.")

    elif required_year is not None:
        reasons.append("Candidate passing year is not available.")

    # 7. Technology
    required_technology = normalize(job.get("technology"))
    candidate_technology = normalize(candidate.get("technology"))

    if (
        required_technology
        and candidate_technology != required_technology
    ):
        reasons.append("Candidate technology does not match.")

    # 8. Required Skills
    required_skills = {
        normalize(skill)
        for skill in (job.get("required_skills") or "").split(",")
        if normalize(skill)
    }

    available_skills = {
        normalize(skill)
        for skill in (candidate.get("skills") or "").split(",")
        if normalize(skill)
    }

    missing_skills = required_skills - available_skills

    if missing_skills:
        reasons.append(
            "Missing required skills: "
            + ", ".join(sorted(missing_skills))
        )

    # 9. Backlogs
    candidate_backlogs = int(candidate.get("backlogs") or 0)
    maximum_backlogs = int(job.get("max_backlogs") or 0)

    if candidate_backlogs > maximum_backlogs:
        reasons.append("Candidate has more backlogs than allowed.")

    # 10. Application Deadline
    deadline = parse_date(job.get("deadline"))

    if deadline and deadline < date.today():
        reasons.append("Job application deadline has passed.")

    return len(reasons) == 0, reasons

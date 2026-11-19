
from datetime import date, datetime, timedelta

from models.company import Company
from models.candidate import Candidate
from models.job import Job
from models.application import Application
from models.interview import Interview

from services.company_service import add_company, delete_company
from services.candidate_service import add_candidate, delete_candidate
from services.job_service import add_job, delete_job
from services.application_service import add_application, delete_application

from services.interview_service import (
    schedule_interview,
    get_interview,
    get_all_interviews,
    update_interview,
    update_interview_result,
    delete_interview
)

company_id = None
candidate_id = None
job_id = None
application_id = None
interview_id = None

try:
    unique = datetime.now().strftime("%Y%m%d%H%M%S%f")

    # 1. Create Company
    company = Company(
        company_name="Interview Test Company",
        email=f"company{unique}@example.com",
        mobile="9876543210",
        location="Pune"
    )

    company_id = add_company(company)
    print("1. Test Company Created!")

    # 2. Create Candidate
    candidate = Candidate(
        full_name="Interview Test Candidate",
        email=f"candidate{unique}@example.com",
        mobile="9876543211",
        qualification="BCA",
        percentage=80,
        passing_year=2026,
        technology="Python",
        skills="Python, Django, SQL",
        backlogs=0
    )

    candidate_id = add_candidate(candidate)
    print("2. Test Candidate Created!")

    # 3. Create Job
    today = date.today()

    job = Job(
        company_id=company_id,
        job_title="Python Developer",
        openings=2,
        qualification_required="BCA",
        minimum_percentage=60,
        passing_year=2026,
        technology="Python",
        required_skills="Python, Django",
        max_backlogs=0,
        min_package=3.5,
        max_package=6.0,
        posted_date=today.isoformat(),
        deadline=(today + timedelta(days=30)).isoformat(),
        job_status="Open"
    )

    job_id = add_job(job)
    print("3. Test Job Created!")

    # 4. Create Application
    application = Application(
        candidate_id=candidate_id,
        job_id=job_id
    )

    application_id = add_application(application)
    print("4. Test Application Created!")

    # 5. Schedule Interview
    future_date = datetime.now() + timedelta(days=2)

    interview = Interview(
        application_id=application_id,
        round_name="Technical Round",
        interview_date=future_date.strftime("%Y-%m-%d %H:%M:%S"),
        interviewer="HR Manager",
        feedback="",
        result="Pending"
    )

    interview_id = schedule_interview(interview)
    print("5. Interview Scheduled Successfully!")

    # 6. View Interview
    details = get_interview(interview_id)
    print("6. Interview Details:", details)

    # 7. View All Interviews
    interviews = get_all_interviews()
    print("7. Total Interviews:", len(interviews))

    # 8. Update Interview
    updated_interview = Interview(
        application_id=application_id,
        round_name="Final Technical Round",
        interview_date=(datetime.now() + timedelta(days=3)).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        interviewer="Senior Technical Manager",
        feedback="Good technical knowledge",
        result="Next Round"
    )

    update_interview(interview_id, updated_interview)
    print("8. Interview Updated Successfully!")

    # 9. Update Result
    update_interview_result(interview_id, "Selected")

    updated = get_interview(interview_id)
    print("9. Updated Result:", updated["result"])

    # 10. Delete Interview
    delete_interview(interview_id)
    interview_id = None
    print("10. Interview Deleted Successfully!")

except Exception as error:
    print("Testing Error:", error)

finally:
    if interview_id is not None:
        try:
            delete_interview(interview_id)
        except Exception:
            pass

    if application_id is not None:
        try:
            delete_application(application_id)
        except Exception:
            pass

    if job_id is not None:
        try:
            delete_job(job_id)
        except Exception:
            pass

    if candidate_id is not None:
        try:
            delete_candidate(candidate_id)
        except Exception:
            pass

    if company_id is not None:
        try:
            delete_company(company_id)
        except Exception:
            pass

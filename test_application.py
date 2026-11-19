
from datetime import date, timedelta, datetime

from models.company import Company
from models.candidate import Candidate
from models.job import Job
from models.application import Application

from services.company_service import add_company, delete_company
from services.candidate_service import add_candidate, delete_candidate
from services.job_service import add_job, delete_job
from services.application_service import (
    add_application,
    get_application,
    get_all_applications,
    update_application_status,
    delete_application
)

company_id = None
candidate_id = None
job_id = None
application_id = None

try:
    unique = datetime.now().strftime("%Y%m%d%H%M%S%f")

    # 1. Create temporary company
    company = Company(
        company_name="Application Test Company",
        contact_person="Test Manager",
        email=f"company{unique}@example.com",
        mobile="9876543210",
        location="Pune"
    )

    company_id = add_company(company)
    print("1. Test Company Created!")

    # 2. Create temporary candidate
    candidate = Candidate(
        full_name="Application Test Candidate",
        email=f"candidate{unique}@example.com",
        mobile="9876543211",
        qualification="BCA",
        percentage=80.0,
        passing_year=2026,
        technology="Python",
        skills="Python, Django, MySQL",
        backlogs=0
    )

    candidate_id = add_candidate(candidate)
    print("2. Test Candidate Created!")

    # 3. Create temporary job
    today = date.today()

    job = Job(
        company_id=company_id,
        job_title="Python Developer",
        openings=2,
        qualification_required="BCA",
        minimum_percentage=60,
        passing_year=2026,
        technology="Python",
        required_skills="Python, Django, SQL",
        max_backlogs=0,
        min_package=3.5,
        max_package=6.0,
        posted_date=today.isoformat(),
        deadline=(today + timedelta(days=30)).isoformat(),
        job_status="Open"
    )

    job_id = add_job(job)
    print("3. Test Job Created!")

    # 4. Apply for job
    application = Application(
        candidate_id=candidate_id,
        job_id=job_id
    )

    application_id = add_application(application)
    print("4. Application Added Successfully!")

    # 5. View application
    details = get_application(application_id)
    print("5. Application Details:", details)

    # 6. View all applications
    applications = get_all_applications()
    print("6. Total Applications:", len(applications))

    # 7. Update application status
    update_application_status(application_id, "Shortlisted")

    updated = get_application(application_id)
    print("7. Updated Status:", updated["application_status"])

    # 8. Test duplicate application prevention
    try:
        add_application(application)
        print("8. ERROR: Duplicate application was accepted!")

    except ValueError as error:
        print("8. Duplicate Prevention Working:", error)

    # 9. Delete application
    delete_application(application_id)
    application_id = None
    print("9. Application Deleted Successfully!")

except Exception as error:
    print("Testing Error:", error)

finally:
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


from datetime import date, timedelta
from models.company import Company
from models.job import Job
from services.company_service import add_company, delete_company
from services.job_service import (
    add_job,
    get_job,
    get_all_jobs,
    update_job,
    delete_job
)

company_id = None
job_id = None

try:
    # Create a test company first
    company = Company(
        company_name="Test Job Company",
        contact_person="Test Manager",
        email="jobtest@example.com",
        mobile="9876543210",
        location="Pune"
    )

    company_id = add_company(company)
    print("1. Test Company Created Successfully!")

    today = date.today()
    deadline = today + timedelta(days=30)

    job = Job(
        company_id=company_id,
        job_title="Python Developer",
        openings=3,
        qualification_required="BCA",
        minimum_percentage=60,
        passing_year=2026,
        technology="Python",
        required_skills="Python, Django, MySQL",
        max_backlogs=0,
        min_package=3.5,
        max_package=6.0,
        posted_date=today.isoformat(),
        deadline=deadline.isoformat(),
        job_status="Open"
    )

    job_id = add_job(job)
    print("2. Job Added Successfully!")

    data = get_job(job_id)
    print("3. Job Details:", data)

    jobs = get_all_jobs()
    print("4. Total Jobs:", len(jobs))

    updated_job = Job(
        company_id=company_id,
        job_title="Senior Python Developer",
        openings=5,
        qualification_required="BCA",
        minimum_percentage=65,
        passing_year=2026,
        technology="Python",
        required_skills="Python, Django, REST API",
        max_backlogs=0,
        min_package=4.0,
        max_package=8.0,
        posted_date=today.isoformat(),
        deadline=deadline.isoformat(),
        job_status="Open"
    )

    update_job(job_id, updated_job)
    print("5. Job Updated Successfully!")

    delete_job(job_id)
    job_id = None
    print("6. Job Deleted Successfully!")

except Exception as error:
    print("Testing Error:", error)

finally:
    if job_id is not None:
        try:
            delete_job(job_id)
        except Exception:
            pass

    if company_id is not None:
        try:
            delete_company(company_id)
        except Exception:
            pass

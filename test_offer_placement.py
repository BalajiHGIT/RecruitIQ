
from datetime import date, timedelta, datetime

from models.company import Company
from models.candidate import Candidate
from models.job import Job
from models.application import Application
from models.offer import Offer
from models.placement import Placement

from services.company_service import add_company, delete_company
from services.candidate_service import add_candidate, delete_candidate
from services.job_service import add_job, delete_job
from services.application_service import (
    add_application,
    update_application_status,
    delete_application
)
from services.offer_service import (
    add_offer,
    get_offer,
    get_all_offers,
    update_offer,
    update_offer_status,
    delete_offer
)
from services.placement_service import (
    add_placement,
    get_placement,
    get_all_placements,
    update_placement,
    delete_placement
)

company_id = None
candidate_id = None
job_id = None
application_id = None
offer_id = None
placement_id = None

try:
    unique = datetime.now().strftime("%Y%m%d%H%M%S%f")
    today = date.today()
    joining = today + timedelta(days=30)

    # 1. Create Company
    company_id = add_company(Company(
        company_name="Offer Test Company",
        email=f"company{unique}@example.com",
        mobile="9876543210",
        location="Pune"
    ))
    print("1. Company Created Successfully!")

    # 2. Create Candidate
    candidate_id = add_candidate(Candidate(
        full_name="Offer Test Candidate",
        email=f"candidate{unique}@example.com",
        mobile="9876543211",
        qualification="BCA",
        percentage=80,
        passing_year=2026,
        technology="Python",
        skills="Python, Django, SQL",
        backlogs=0
    ))
    print("2. Candidate Created Successfully!")

    # 3. Create Job
    job_id = add_job(Job(
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
        deadline=(today + timedelta(days=60)).isoformat(),
        job_status="Open"
    ))
    print("3. Job Created Successfully!")

    # 4. Create Application
    application_id = add_application(Application(
        candidate_id=candidate_id,
        job_id=job_id
    ))
    update_application_status(application_id, "Selected")
    print("4. Application Selected Successfully!")

    # 5. Create Offer
    offer_id = add_offer(Offer(
        application_id=application_id,
        offer_date=today.isoformat(),
        package=4.5,
        offer_status="Pending",
        joining_date=joining.isoformat()
    ))
    print("5. Offer Created Successfully!")

    # 6. View Offer
    print("6. Offer Details:", get_offer(offer_id))

    # 7. View All Offers
    print("7. Total Offers:", len(get_all_offers()))

    # 8. Accept Offer
    update_offer_status(offer_id, "Accepted")
    print("8. Offer Accepted Successfully!")

    # 9. Update Offer
    update_offer(
        offer_id,
        Offer(
            application_id=application_id,
            offer_date=today.isoformat(),
            package=5.0,
            offer_status="Accepted",
            joining_date=joining.isoformat()
        )
    )
    print("9. Offer Updated Successfully!")

    # 10. Create Placement
    placement_id = add_placement(Placement(
        candidate_id=candidate_id,
        company_id=company_id,
        job_id=job_id,
        package=5.0,
        placement_status="Confirmed"
    ))
    print("10. Placement Created Successfully!")

    # 11. View Placement
    print("11. Placement Details:", get_placement(placement_id))

    # 12. View All Placements
    print("12. Total Placements:", len(get_all_placements()))

    # 13. Update Placement
    update_placement(
        placement_id,
        Placement(
            candidate_id=candidate_id,
            company_id=company_id,
            job_id=job_id,
            package=5.0,
            placement_status="Joined",
            joining_date=joining.isoformat()
        )
    )
    print("13. Placement Updated Successfully!")

    # 14. Delete Placement
    delete_placement(placement_id)
    placement_id = None
    print("14. Placement Deleted Successfully!")

    # 15. Delete Offer
    delete_offer(offer_id)
    offer_id = None
    print("15. Offer Deleted Successfully!")

except Exception as error:
    print("Testing Error:", error)

finally:
    if placement_id is not None:
        try:
            delete_placement(placement_id)
        except Exception:
            pass

    if offer_id is not None:
        try:
            delete_offer(offer_id)
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

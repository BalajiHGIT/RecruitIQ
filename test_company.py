from datetime import datetime

from models.company import Company
from services.company_service import (
    add_company,
    get_company,
    get_all_companies,
    update_company,
    delete_company
)

company_id = None

try:
    email = f"test{datetime.now():%Y%m%d%H%M%S%f}@example.com"

    company = Company(
        company_name="TCS Test Company",
        contact_person="Test Manager",
        email=email,
        mobile="9876543210",
        location="Pune"
    )

    company_id = add_company(company)
    print("1. Company Added Successfully!")

    data = get_company(company_id)
    print("2. Company Details:", data)

    companies = get_all_companies()
    print("3. Total Companies:", len(companies))

    updated_company = Company(
        company_name="TCS Updated",
        contact_person="Updated Manager",
        email=email,
        mobile="9876543210",
        location="Mumbai"
    )

    update_company(company_id, updated_company)
    print("4. Company Updated Successfully!")

    delete_company(company_id)
    company_id = None
    print("5. Company Deleted Successfully!")

except Exception as error:
    print("Testing Error:", error)

finally:
    if company_id is not None:
        try:
            delete_company(company_id)
        except Exception:
            pass
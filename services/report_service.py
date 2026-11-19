
"""Reporting service for Recruitment and Placement Management System."""

from database import get_connection


def _fetch_all(query):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def _fetch_one(query):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def report_menu():
    return [
        "Dashboard Summary",
        "Candidate Summary",
        "Company and Job Summary",
        "Application Status Summary",
        "Interview Result Summary",
        "Offer Status Summary",
        "Placement Summary"
    ]


def get_dashboard_summary():
    query = """
    SELECT
        (SELECT COUNT(*) FROM candidates) AS total_candidates,
        (SELECT COUNT(*) FROM companies) AS total_companies,
        (SELECT COUNT(*) FROM jobs) AS total_jobs,
        (SELECT COUNT(*) FROM jobs WHERE job_status='Open') AS open_jobs,
        (SELECT COUNT(*) FROM applications) AS total_applications,
        (SELECT COUNT(*) FROM interviews) AS total_interviews,
        (SELECT COUNT(*) FROM offers) AS total_offers,
        (SELECT COUNT(*) FROM placements
         WHERE placement_status IN ('Confirmed', 'Joined')
        ) AS total_placements
    """

    return _fetch_one(query)


def get_candidate_summary():
    query = """
    SELECT
        candidate_status,
        COUNT(*) AS total_candidates
    FROM candidates
    GROUP BY candidate_status
    ORDER BY candidate_status
    """

    return _fetch_all(query)


def get_company_job_summary():
    query = """
    SELECT
        c.company_id,
        c.company_name,
        COUNT(j.job_id) AS total_jobs,
        SUM(
            CASE WHEN j.job_status = 'Open'
            THEN 1 ELSE 0 END
        ) AS open_jobs
    FROM companies c
    LEFT JOIN jobs j ON c.company_id = j.company_id
    GROUP BY c.company_id, c.company_name
    ORDER BY c.company_name
    """

    return _fetch_all(query)


def get_application_status_summary():
    query = """
    SELECT
        application_status,
        COUNT(*) AS total_applications
    FROM applications
    GROUP BY application_status
    ORDER BY application_status
    """

    return _fetch_all(query)


def get_interview_result_summary():
    query = """
    SELECT
        result,
        COUNT(*) AS total_interviews
    FROM interviews
    GROUP BY result
    ORDER BY result
    """

    return _fetch_all(query)


def get_offer_status_summary():
    query = """
    SELECT
        offer_status,
        COUNT(*) AS total_offers
    FROM offers
    GROUP BY offer_status
    ORDER BY offer_status
    """

    return _fetch_all(query)


def get_placement_summary():
    query = """
    SELECT
        placement_status,
        COUNT(*) AS total_placements,
        ROUND(AVG(package), 2) AS average_package,
        MAX(package) AS highest_package
    FROM placements
    GROUP BY placement_status
    ORDER BY placement_status
    """

    return _fetch_all(query)


def get_placement_details():
    query = """
    SELECT
        p.placement_id,
        c.full_name,
        co.company_name,
        j.job_title,
        p.package,
        p.joining_date,
        p.placement_status
    FROM placements p
    JOIN candidates c ON p.candidate_id = c.candidate_id
    JOIN companies co ON p.company_id = co.company_id
    JOIN jobs j ON p.job_id = j.job_id
    ORDER BY p.placement_id DESC
    """

    return _fetch_all(query)


def get_all_reports():
    return {
        "dashboard": get_dashboard_summary(),
        "candidates": get_candidate_summary(),
        "companies_jobs": get_company_job_summary(),
        "applications": get_application_status_summary(),
        "interviews": get_interview_result_summary(),
        "offers": get_offer_status_summary(),
        "placements": get_placement_summary(),
        "placement_details": get_placement_details()
    }

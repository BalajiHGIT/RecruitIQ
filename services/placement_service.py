
from datetime import date
from decimal import Decimal
from database import get_connection


VALID_PLACEMENT_STATUSES = ("Confirmed", "Joined", "Cancelled")


def validate_package(min_package, max_package):
    if min_package < 0 or max_package < 0:
        raise ValueError("Package cannot be negative.")

    if min_package > max_package:
        raise ValueError("Minimum package cannot exceed maximum package.")


def validate_placement(placement):
    if placement.candidate_id <= 0:
        raise ValueError("Invalid candidate ID.")

    if placement.company_id <= 0:
        raise ValueError("Invalid company ID.")

    if placement.job_id <= 0:
        raise ValueError("Invalid job ID.")

    if Decimal(str(placement.package)) <= 0:
        raise ValueError("Placement package must be greater than zero.")

    if placement.placement_status not in VALID_PLACEMENT_STATUSES:
        raise ValueError("Invalid placement status.")

    joining_date = (
        date.fromisoformat(placement.joining_date)
        if placement.joining_date else None
    )

    if placement.placement_status == "Joined" and not joining_date:
        raise ValueError("Joining date is required for Joined status.")

    return joining_date


def validate_placement_links(cursor, placement, exclude_id=None):
    cursor.execute(
        """
        SELECT a.application_id, a.application_status,
               j.company_id, j.min_package, j.max_package
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        WHERE a.candidate_id = %s AND a.job_id = %s
        """,
        (placement.candidate_id, placement.job_id)
    )

    application = cursor.fetchone()

    if not application:
        raise ValueError("Candidate application for this job does not exist.")

    if application["company_id"] != placement.company_id:
        raise ValueError("Company does not match the selected job.")

    if application["application_status"] != "Selected":
        raise ValueError("Only selected candidates can be placed.")

    cursor.execute(
        """
        SELECT offer_id FROM offers
        WHERE application_id = %s AND offer_status = 'Accepted'
        """,
        (application["application_id"],)
    )

    if not cursor.fetchone():
        raise ValueError("Candidate must have an accepted offer.")

    package = Decimal(str(placement.package))
    minimum = application["min_package"]
    maximum = application["max_package"]

    if minimum is not None and package < minimum:
        raise ValueError("Placement package is below job minimum.")

    if maximum is not None and package > maximum:
        raise ValueError("Placement package exceeds job maximum.")

    query = """
        SELECT placement_id FROM placements
        WHERE candidate_id = %s AND job_id = %s
    """
    values = [placement.candidate_id, placement.job_id]

    if exclude_id is not None:
        query += " AND placement_id != %s"
        values.append(exclude_id)

    cursor.execute(query, tuple(values))

    if cursor.fetchone():
        raise ValueError("Placement already exists for this candidate and job.")


def add_placement(placement):
    joining_date = validate_placement(placement)
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        validate_placement_links(cursor, placement)

        cursor.execute(
            """
            INSERT INTO placements
            (candidate_id, company_id, job_id, joining_date,
             package, placement_status)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                placement.candidate_id,
                placement.company_id,
                placement.job_id,
                joining_date,
                placement.package,
                placement.placement_status
            )
        )

        connection.commit()
        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def get_all_placements():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT p.*, c.full_name, co.company_name, j.job_title
            FROM placements p
            JOIN candidates c ON p.candidate_id = c.candidate_id
            JOIN companies co ON p.company_id = co.company_id
            JOIN jobs j ON p.job_id = j.job_id
            ORDER BY p.placement_id DESC
            """
        )

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_placement(placement_id):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM placements WHERE placement_id=%s",
            (placement_id,)
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def update_placement(placement_id, placement):
    joining_date = validate_placement(placement)
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        validate_placement_links(cursor, placement, placement_id)

        cursor.execute(
            """
            UPDATE placements
            SET candidate_id=%s,
                company_id=%s,
                job_id=%s,
                joining_date=%s,
                package=%s,
                placement_status=%s
            WHERE placement_id=%s
            """,
            (
                placement.candidate_id,
                placement.company_id,
                placement.job_id,
                joining_date,
                placement.package,
                placement.placement_status,
                placement_id
            )
        )

        connection.commit()
        return cursor.rowcount > 0

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def delete_placement(placement_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM placements WHERE placement_id=%s",
            (placement_id,)
        )

        connection.commit()
        return cursor.rowcount > 0

    finally:
        cursor.close()
        connection.close()

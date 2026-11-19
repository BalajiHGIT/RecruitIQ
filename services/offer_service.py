
from datetime import date
from database import get_connection


VALID_OFFER_STATUSES = ("Pending", "Accepted", "Declined")


def validate_offer(offer):
    if offer.application_id <= 0:
        raise ValueError("Invalid application ID.")

    if offer.package <= 0:
        raise ValueError("Offer package must be greater than zero.")

    if offer.offer_status not in VALID_OFFER_STATUSES:
        raise ValueError("Invalid offer status.")

    offer_date = (
        date.fromisoformat(offer.offer_date)
        if offer.offer_date else date.today()
    )

    joining_date = (
        date.fromisoformat(offer.joining_date)
        if offer.joining_date else None
    )

    if joining_date and joining_date < offer_date:
        raise ValueError("Joining date cannot be before offer date.")

    return offer_date, joining_date


def validate_application_offer(cursor, offer):
    cursor.execute(
        """
        SELECT a.application_status, j.min_package, j.max_package
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        WHERE a.application_id = %s
        """,
        (offer.application_id,)
    )

    application = cursor.fetchone()

    if not application:
        raise ValueError("Application does not exist.")

    if application["application_status"] != "Selected":
        raise ValueError("Offer can only be created for selected applications.")

    minimum = application["min_package"]
    maximum = application["max_package"]

    if minimum is not None and offer.package < minimum:
        raise ValueError("Offer package is below the job minimum package.")

    if maximum is not None and offer.package > maximum:
        raise ValueError("Offer package exceeds the job maximum package.")


def add_offer(offer):
    offer_date, joining_date = validate_offer(offer)
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        validate_application_offer(cursor, offer)

        cursor.execute(
            "SELECT offer_id FROM offers WHERE application_id = %s",
            (offer.application_id,)
        )

        if cursor.fetchone():
            raise ValueError("An offer already exists for this application.")

        cursor.execute(
            """
            INSERT INTO offers
            (application_id, offer_date, package, offer_status, joining_date)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                offer.application_id,
                offer_date,
                offer.package,
                offer.offer_status,
                joining_date
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


def get_all_offers():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT o.*, c.full_name, j.job_title, co.company_name
            FROM offers o
            JOIN applications a ON o.application_id = a.application_id
            JOIN candidates c ON a.candidate_id = c.candidate_id
            JOIN jobs j ON a.job_id = j.job_id
            JOIN companies co ON j.company_id = co.company_id
            ORDER BY o.offer_id DESC
            """
        )

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_offer(offer_id):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM offers WHERE offer_id = %s",
            (offer_id,)
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def update_offer(offer_id, offer):
    offer_date, joining_date = validate_offer(offer)
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        validate_application_offer(cursor, offer)

        cursor.execute(
            """
            UPDATE offers
            SET application_id=%s,
                offer_date=%s,
                package=%s,
                offer_status=%s,
                joining_date=%s
            WHERE offer_id=%s
            """,
            (
                offer.application_id,
                offer_date,
                offer.package,
                offer.offer_status,
                joining_date,
                offer_id
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


def update_offer_status(offer_id, new_status):
    if new_status not in VALID_OFFER_STATUSES:
        raise ValueError("Invalid offer status.")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "UPDATE offers SET offer_status=%s WHERE offer_id=%s",
            (new_status, offer_id)
        )

        connection.commit()
        return cursor.rowcount > 0

    finally:
        cursor.close()
        connection.close()


def delete_offer(offer_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM offers WHERE offer_id=%s",
            (offer_id,)
        )

        connection.commit()
        return cursor.rowcount > 0

    finally:
        cursor.close()
        connection.close()

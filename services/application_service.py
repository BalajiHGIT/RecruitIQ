from datetime import date
from database import get_connection
from mysql.connector import IntegrityError


VALID_STATUSES = (
    "Applied",
    "Shortlisted",
    "Rejected",
    "Selected",
    "Withdrawn"
)


def prevent_duplicate_application(candidate_id, job_id, existing_pairs):
    if (candidate_id, job_id) in existing_pairs:
        raise ValueError("This candidate has already applied for this job.")


def add_application(application):
    if application.application_status not in VALID_STATUSES:
        raise ValueError("Invalid application status.")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT candidate_status FROM candidates WHERE candidate_id=%s",
            (application.candidate_id,)
        )
        candidate = cursor.fetchone()

        if not candidate:
            raise ValueError("Candidate does not exist.")

        if candidate["candidate_status"] != "Active":
            raise ValueError("Candidate is not active.")

        cursor.execute(
            "SELECT job_status, deadline FROM jobs WHERE job_id=%s",
            (application.job_id,)
        )
        job = cursor.fetchone()

        if not job:
            raise ValueError("Job does not exist.")

        if job["job_status"] != "Open":
            raise ValueError("Job is not open.")

        if job["deadline"] and job["deadline"] < date.today():
            raise ValueError("Application deadline has passed.")

        cursor.execute(
            """
            SELECT application_id FROM applications
            WHERE candidate_id=%s AND job_id=%s
            """,
            (application.candidate_id, application.job_id)
        )

        if cursor.fetchone():
            raise ValueError("Duplicate application not allowed.")

        cursor.execute(
            """
            INSERT INTO applications
            (candidate_id, job_id, application_date, application_status)
            VALUES (%s, %s, %s, %s)
            """,
            (
                application.candidate_id,
                application.job_id,
                date.today(),
                application.application_status
            )
        )

        connection.commit()
        return cursor.lastrowid

    except IntegrityError as exc:
        connection.rollback()
        raise ValueError("Duplicate application or invalid candidate/job.") from exc

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def get_all_applications():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
        SELECT a.application_id, c.full_name, j.job_title,
               co.company_name, a.application_date,
               a.application_status
        FROM applications a
        JOIN candidates c ON a.candidate_id = c.candidate_id
        JOIN jobs j ON a.job_id = j.job_id
        JOIN companies co ON j.company_id = co.company_id
        ORDER BY a.application_id DESC
        """

        cursor.execute(query)
        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_application(application_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM applications WHERE application_id=%s",
            (application_id,)
        )
        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def update_application_status(application_id, new_status):
    if new_status not in VALID_STATUSES:
        raise ValueError("Invalid application status.")

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE applications
            SET application_status=%s
            WHERE application_id=%s
            """,
            (new_status, application_id)
        )

        connection.commit()
        return cursor.rowcount > 0

    finally:
        cursor.close()
        connection.close()


def delete_application(application_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM applications WHERE application_id=%s",
            (application_id,)
        )

        connection.commit()
        return cursor.rowcount > 0

    except IntegrityError as exc:
        connection.rollback()
        raise ValueError(
            "Cannot delete application because interview or offer records are linked."
        ) from exc

    finally:
        cursor.close()
        connection.close()
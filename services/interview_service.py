
from datetime import datetime
from database import get_connection


VALID_RESULTS = (
    "Pending",
    "Selected",
    "Rejected",
    "Next Round"
)


def validate_interview_date(value):
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.strip())
        except ValueError:
            raise ValueError(
                "Invalid date format. Use YYYY-MM-DD HH:MM:SS."
            )

    if not isinstance(value, datetime):
        raise ValueError("Invalid interview date.")

    if value.tzinfo is not None:
        raise ValueError("Use local date and time without timezone.")

    if value < datetime.now():
        raise ValueError("Interview date cannot be in the past.")

    return value


def validate_interview(interview):
    if not interview.round_name.strip():
        raise ValueError("Interview round name is required.")

    if interview.result not in VALID_RESULTS:
        raise ValueError("Invalid interview result.")

    return validate_interview_date(interview.interview_date)


def schedule_interview(interview):
    interview_date = validate_interview(interview)
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT application_id FROM applications WHERE application_id=%s",
            (interview.application_id,)
        )

        if not cursor.fetchone():
            raise ValueError("Application does not exist.")

        query = """
        INSERT INTO interviews
        (application_id, round_name, interview_date,
         interviewer, feedback, result)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            interview.application_id,
            interview.round_name,
            interview_date,
            interview.interviewer,
            interview.feedback,
            interview.result
        )

        cursor.execute(query, values)
        connection.commit()

        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def get_all_interviews():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT
            i.interview_id,
            i.application_id,
            c.full_name,
            j.job_title,
            co.company_name,
            i.round_name,
            i.interview_date,
            i.interviewer,
            i.feedback,
            i.result
        FROM interviews i
        JOIN applications a ON i.application_id = a.application_id
        JOIN candidates c ON a.candidate_id = c.candidate_id
        JOIN jobs j ON a.job_id = j.job_id
        JOIN companies co ON j.company_id = co.company_id
        ORDER BY i.interview_date DESC
        """

        cursor.execute(query)
        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_interview(interview_id):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM interviews WHERE interview_id=%s",
            (interview_id,)
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def update_interview(interview_id, interview):
    interview_date = validate_interview(interview)
    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
        UPDATE interviews
        SET round_name=%s,
            interview_date=%s,
            interviewer=%s,
            feedback=%s,
            result=%s
        WHERE interview_id=%s
        """

        values = (
            interview.round_name,
            interview_date,
            interview.interviewer,
            interview.feedback,
            interview.result,
            interview_id
        )

        cursor.execute(query, values)
        connection.commit()

        return cursor.rowcount > 0

    finally:
        cursor.close()
        connection.close()


def update_interview_result(interview_id, new_result):
    if new_result not in VALID_RESULTS:
        raise ValueError("Invalid interview result.")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE interviews
            SET result=%s
            WHERE interview_id=%s
            """,
            (new_result, interview_id)
        )

        connection.commit()
        return cursor.rowcount > 0

    finally:
        cursor.close()
        connection.close()


def delete_interview(interview_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM interviews WHERE interview_id=%s",
            (interview_id,)
        )

        connection.commit()
        return cursor.rowcount > 0

    finally:
        cursor.close()
        connection.close()

import re
from database import get_connection
from mysql.connector import IntegrityError


def validate_candidate(candidate):
    if not candidate.full_name.strip():
        raise ValueError("Candidate name is required.")

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", candidate.email):
        raise ValueError("Invalid email address.")

    if not re.fullmatch(r"[0-9]{10}", candidate.mobile):
        raise ValueError("Mobile number must contain 10 digits.")

    if not 0 <= float(candidate.percentage) <= 100:
        raise ValueError("Percentage must be between 0 and 100.")

    if candidate.backlogs < 0:
        raise ValueError("Backlogs cannot be negative.")


def add_candidate(candidate):
    validate_candidate(candidate)
    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
        INSERT INTO candidates
        (full_name, email, mobile, qualification,
         percentage, passing_year, technology, skills, backlogs)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            candidate.full_name,
            candidate.email,
            candidate.mobile,
            candidate.qualification,
            candidate.percentage,
            candidate.passing_year,
            candidate.technology,
            candidate.skills,
            candidate.backlogs
        )

        cursor.execute(query, values)
        connection.commit()

        return cursor.lastrowid

    except IntegrityError:
        connection.rollback()
        raise ValueError("Candidate email already exists.")

    finally:
        if 'cursor' in locals():
            cursor.close()
        connection.close()


def get_all_candidates():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM candidates ORDER BY candidate_id DESC")

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_candidate(candidate_id):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM candidates WHERE candidate_id = %s",
            (candidate_id,)
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def update_candidate(candidate_id, candidate):
    validate_candidate(candidate)
    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
        UPDATE candidates
        SET full_name=%s, email=%s, mobile=%s,
            qualification=%s, percentage=%s,
            passing_year=%s, technology=%s,
            skills=%s, backlogs=%s
        WHERE candidate_id=%s
        """

        values = (
            candidate.full_name,
            candidate.email,
            candidate.mobile,
            candidate.qualification,
            candidate.percentage,
            candidate.passing_year,
            candidate.technology,
            candidate.skills,
            candidate.backlogs,
            candidate_id
        )

        cursor.execute(query, values)
        connection.commit()

        return cursor.rowcount > 0

    except IntegrityError:
        connection.rollback()
        raise ValueError("Candidate email already exists.")

    finally:
        cursor.close()
        connection.close()


def delete_candidate(candidate_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM candidates WHERE candidate_id = %s",
            (candidate_id,)
        )

        connection.commit()
        return cursor.rowcount > 0

    finally:
        cursor.close()
        connection.close()
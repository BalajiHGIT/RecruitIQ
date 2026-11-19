
import re
from datetime import date
from database import get_connection
from mysql.connector import IntegrityError


def validate_job(job):
    if not job.job_title.strip():
        raise ValueError("Job title is required.")

    if job.openings <= 0:
        raise ValueError("Openings must be greater than zero.")

    if not 0 <= job.minimum_percentage <= 100:
        raise ValueError("Minimum percentage must be between 0 and 100.")

    if job.max_backlogs < 0:
        raise ValueError("Maximum backlogs cannot be negative.")

    if (
        job.min_package is not None
        and job.max_package is not None
        and job.min_package > job.max_package
    ):
        raise ValueError("Minimum package cannot exceed maximum package.")

    if job.min_package is not None and job.min_package < 0:
        raise ValueError("Package cannot be negative.")

    if job.max_package is not None and job.max_package < 0:
        raise ValueError("Package cannot be negative.")

    if job.posted_date and job.deadline:
        posted = date.fromisoformat(job.posted_date)
        deadline = date.fromisoformat(job.deadline)

        if deadline < posted:
            raise ValueError("Deadline cannot be before posted date.")

    if job.job_status not in ("Open", "Closed", "On Hold"):
        raise ValueError("Invalid job status.")


def add_job(job):
    validate_job(job)
    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
        INSERT INTO jobs (
            company_id, job_title, qualification_required,
            minimum_percentage, passing_year, technology,
            required_skills, max_backlogs, openings,
            min_package, max_package, posted_date,
            deadline, job_status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s)
        """

        values = (
            job.company_id,
            job.job_title,
            job.qualification_required,
            job.minimum_percentage,
            job.passing_year,
            job.technology,
            job.required_skills,
            job.max_backlogs,
            job.openings,
            job.min_package,
            job.max_package,
            job.posted_date,
            job.deadline,
            job.job_status
        )

        cursor.execute(query, values)
        connection.commit()
        return cursor.lastrowid

    except IntegrityError as exc:
        connection.rollback()
        raise ValueError(
            "Invalid company ID or job data. Check the company exists."
        ) from exc

    finally:
        if 'cursor' in locals():
            cursor.close()
        connection.close()


def get_all_jobs():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT j.*, c.company_name
        FROM jobs j
        JOIN companies c ON j.company_id = c.company_id
        ORDER BY j.job_id DESC
        """

        cursor.execute(query)
        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_job(job_id):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM jobs WHERE job_id = %s",
            (job_id,)
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def update_job(job_id, job):
    validate_job(job)
    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
        UPDATE jobs SET
            company_id = %s,
            job_title = %s,
            qualification_required = %s,
            minimum_percentage = %s,
            passing_year = %s,
            technology = %s,
            required_skills = %s,
            max_backlogs = %s,
            openings = %s,
            min_package = %s,
            max_package = %s,
            posted_date = %s,
            deadline = %s,
            job_status = %s
        WHERE job_id = %s
        """

        values = (
            job.company_id,
            job.job_title,
            job.qualification_required,
            job.minimum_percentage,
            job.passing_year,
            job.technology,
            job.required_skills,
            job.max_backlogs,
            job.openings,
            job.min_package,
            job.max_package,
            job.posted_date,
            job.deadline,
            job.job_status,
            job_id
        )

        cursor.execute(query, values)
        connection.commit()
        return cursor.rowcount > 0

    except IntegrityError as exc:
        connection.rollback()
        raise ValueError("Invalid company ID or job data.") from exc

    finally:
        cursor.close()
        connection.close()


def delete_job(job_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM jobs WHERE job_id = %s",
            (job_id,)
        )

        connection.commit()
        return cursor.rowcount > 0

    except IntegrityError as exc:
        connection.rollback()
        raise ValueError(
            "Cannot delete this job because applications are linked to it."
        ) from exc

    finally:
        cursor.close()
        connection.close()

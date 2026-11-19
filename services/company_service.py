import re
from database import get_connection
from mysql.connector import IntegrityError


def validate_company(company):
    if not company.company_name.strip():
        raise ValueError("Company name is required.")

    if company.email and not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+", company.email
    ):
        raise ValueError("Invalid company email.")

    if company.mobile and not re.fullmatch(
        r"[0-9]{10}", company.mobile
    ):
        raise ValueError("Mobile number must contain 10 digits.")


def add_company(company):
    validate_company(company)
    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
        INSERT INTO companies
        (company_name, contact_person, email, mobile, location)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            company.company_name,
            company.contact_person,
            company.email,
            company.mobile,
            company.location
        )

        cursor.execute(query, values)
        connection.commit()

        return cursor.lastrowid

    finally:
        cursor.close()
        connection.close()


def get_all_companies():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM companies ORDER BY company_id DESC"
        )
        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_company(company_id):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM companies WHERE company_id = %s",
            (company_id,)
        )
        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def update_company(company_id, company):
    validate_company(company)
    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
        UPDATE companies
        SET company_name=%s,
            contact_person=%s,
            email=%s,
            mobile=%s,
            location=%s
        WHERE company_id=%s
        """

        values = (
            company.company_name,
            company.contact_person,
            company.email,
            company.mobile,
            company.location,
            company_id
        )

        cursor.execute(query, values)
        connection.commit()

        return cursor.rowcount > 0

    finally:
        cursor.close()
        connection.close()


def delete_company(company_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM companies WHERE company_id = %s",
            (company_id,)
        )

        connection.commit()
        return cursor.rowcount > 0

    except IntegrityError:
        connection.rollback()
        raise ValueError(
            "Cannot delete company because jobs are linked to it."
        )

    finally:
        cursor.close()
        connection.close() 
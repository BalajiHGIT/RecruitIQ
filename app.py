
"""Recruitment and Placement Management System - Flask Backend."""

import re
import os
from dotenv import load_dotenv

load_dotenv()
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, session, redirect, url_for
from mysql.connector import Error, IntegrityError

from database import get_connection
from werkzeug.utils import secure_filename

from utils.resume_screening.resume_parser import extract_resume_text
from utils.resume_screening.skill_extractor import extract_skills
from utils.resume_screening.matching_engine import calculate_match_score

from models.resume_screening import ResumeScreening

from models.company import Company
from models.job import Job
from models.application import Application
from models.interview import Interview
from models.offer import Offer
from models.placement import Placement

from services.company_service import (
    add_company,
    get_company,
    update_company,
    delete_company
)

from services.job_service import (
    add_job,
    get_all_jobs,
    get_job,
    update_job,
    delete_job
)

from services.application_service import (
    add_application,
    get_all_applications,
    get_application,
    update_application_status,
    delete_application
)

from services.interview_service import (
    schedule_interview,
    get_all_interviews,
    get_interview,
    update_interview,
    update_interview_result,
    delete_interview
)

from services.offer_service import (
    add_offer,
    get_all_offers,
    get_offer,
    update_offer,
    update_offer_status,
    delete_offer
)
from services.placement_service import (
    add_placement,
    get_all_placements,
    get_placement,
    update_placement,
    delete_placement
)


app = Flask(__name__)
app.secret_key = "recruitpro_secret_key_2026"

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

UPLOAD_FOLDER = BASE_DIR / "uploads" / "resumes"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_RESUME_EXTENSIONS = {"pdf", "docx"}


def allowed_resume_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_RESUME_EXTENSIONS
    )


# ---------------- FRONTEND ROUTES ----------------

# ---------------- LOGIN PROTECTION ----------------

@app.before_request
def require_login():

    allowed_routes = ["login", "api_login", "static"]

    if request.endpoint in allowed_routes:
        return None

    # Allow frontend CSS, JavaScript and image files
    if request.path.startswith((
        "/css/",
        "/js/",
        "/images/",
        "/assets/"
    )):
        return None

    if request.path.lower().endswith((
        ".css", ".js", ".png", ".jpg",
        ".jpeg", ".svg", ".ico", ".woff", ".woff2"
    )):
        return None

    if not session.get("logged_in"):
        if request.path.startswith("/api/"):
            return jsonify({
                "success": False,
                "message": "Please login first."
            }), 401

        return redirect("/login")

    return None
# ---------------- LOGIN AUTHENTICATION ----------------

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            session["user_email"] = email
            return redirect("/")

        return redirect("/login?error=1")

    return send_from_directory(FRONTEND_DIR, "login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip()
    password = data.get("password", "")

    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        session["logged_in"] = True
        session["user_email"] = email
        return jsonify({"success": True, "message": "Login successful"})

    return jsonify({"success": False, "message": "Invalid email or password"}), 401

@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "dashboard.html")


@app.route("/<path:filename>")
def frontend_pages(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# ---------------- DATA HELPERS ----------------

def serialize_candidate(candidate):
    result = {}

    for key, value in candidate.items():
        if isinstance(value, (date, datetime)):
            result[key] = value.isoformat()
        elif isinstance(value, Decimal):
            result[key] = float(value)
        else:
            result[key] = value

    return result


def validate_candidate_data(data):
    full_name = str(data.get("full_name") or "").strip()
    email = str(data.get("email") or "").strip().lower()
    mobile = str(data.get("mobile") or "").strip()

    if not full_name:
        raise ValueError("Full name is required.")

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValueError("Enter a valid email address.")

    if not re.fullmatch(r"[0-9]{10}", mobile):
        raise ValueError("Mobile number must contain exactly 10 digits.")

    percentage = data.get("percentage")
    if percentage in ("", None):
        percentage = None
    else:
        try:
            percentage = float(percentage)
        except (TypeError, ValueError):
            raise ValueError("Percentage must be a number.")

        if not 0 <= percentage <= 100:
            raise ValueError("Percentage must be between 0 and 100.")

    passing_year = data.get("passing_year")
    if passing_year in ("", None):
        passing_year = None
    else:
        try:
            passing_year = int(passing_year)
        except (TypeError, ValueError):
            raise ValueError("Passing year must be a whole number.")

        if not 1950 <= passing_year <= 2100:
            raise ValueError("Enter a valid passing year.")

    backlogs = data.get("backlogs", 0)

    try:
        backlogs = int(backlogs)
    except (TypeError, ValueError):
        raise ValueError("Backlogs must be a whole number.")

    if backlogs < 0:
        raise ValueError("Backlogs cannot be negative.")

    return (
        full_name,
        email,
        mobile,
        str(data.get("qualification") or "").strip(),
        percentage,
        passing_year,
        str(data.get("technology") or "").strip(),
        str(data.get("skills") or "").strip(),
        backlogs
    )


# ---------------- DATABASE CONNECTION TEST ----------------

@app.route("/api/health", methods=["GET"])
def database_health():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT DATABASE() AS database_name")
        result = cursor.fetchone()

        return jsonify({
            "success": True,
            "message": "MySQL connection successful.",
            "database": result["database_name"]
        })

    except Error:
        return jsonify({
            "success": False,
            "message": "MySQL connection failed. Check database configuration."
        }), 503

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ---------------- CREATE CANDIDATE ----------------

@app.route("/api/candidates", methods=["POST"])
def add_candidate():
    if not request.is_json:
        return jsonify({
            "success": False,
            "message": "JSON data is required."
        }), 415

    data = request.get_json()

    try:
        values = validate_candidate_data(data)
    except ValueError as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO candidates (
            full_name, email, mobile, qualification,
            percentage, passing_year, technology, skills, backlogs
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, values)
        connection.commit()

        return jsonify({
            "success": True,
            "message": "Candidate registered successfully!",
            "candidate_id": cursor.lastrowid
        }), 201

    except IntegrityError as exc:
        if connection:
            connection.rollback()

        if exc.errno == 1062:
            return jsonify({
                "success": False,
                "message": "This email is already registered."
            }), 409

        return jsonify({
            "success": False,
            "message": "Candidate data conflicts with database records."
        }), 409

    except Error:
        if connection:
            connection.rollback()

        return jsonify({
            "success": False,
            "message": "Database error while saving candidate."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ---------------- VIEW ALL CANDIDATES ----------------

@app.route("/api/candidates", methods=["GET"])
def get_all_candidates():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM candidates
            ORDER BY candidate_id DESC
        """)

        candidates = cursor.fetchall()

        return jsonify({
            "success": True,
            "count": len(candidates),
            "candidates": [
                serialize_candidate(candidate)
                for candidate in candidates
            ]
        })

    except Error:
        return jsonify({
            "success": False,
            "message": "Could not retrieve candidates."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ---------------- VIEW SINGLE CANDIDATE ----------------

@app.route("/api/candidates/<int:candidate_id>", methods=["GET"])
def get_candidate(candidate_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM candidates WHERE candidate_id = %s",
            (candidate_id,)
        )

        candidate = cursor.fetchone()

        if not candidate:
            return jsonify({
                "success": False,
                "message": "Candidate not found."
            }), 404

        return jsonify({
            "success": True,
            "candidate": serialize_candidate(candidate)
        })

    except Error:
        return jsonify({
            "success": False,
            "message": "Could not retrieve candidate."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ---------------- UPDATE CANDIDATE ----------------

@app.route("/api/candidates/<int:candidate_id>", methods=["PUT"])
def update_candidate(candidate_id):
    if not request.is_json:
        return jsonify({
            "success": False,
            "message": "JSON data is required."
        }), 415

    try:
        values = validate_candidate_data(request.get_json())
    except ValueError as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        UPDATE candidates SET
            full_name=%s,
            email=%s,
            mobile=%s,
            qualification=%s,
            percentage=%s,
            passing_year=%s,
            technology=%s,
            skills=%s,
            backlogs=%s
        WHERE candidate_id=%s
        """

        cursor.execute(query, values + (candidate_id,))

        if cursor.rowcount == 0:
            cursor.execute(
                "SELECT candidate_id FROM candidates WHERE candidate_id=%s",
                (candidate_id,)
            )

            if not cursor.fetchone():
                return jsonify({
                    "success": False,
                    "message": "Candidate not found."
                }), 404

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Candidate updated successfully."
        })

    except IntegrityError as exc:
        if connection:
            connection.rollback()

        if exc.errno == 1062:
            return jsonify({
                "success": False,
                "message": "This email is already registered."
            }), 409

        return jsonify({
            "success": False,
            "message": "Candidate data conflicts with database records."
        }), 409

    except Error:
        if connection:
            connection.rollback()

        return jsonify({
            "success": False,
            "message": "Database error while updating candidate."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ---------------- DELETE CANDIDATE ----------------

@app.route("/api/candidates/<int:candidate_id>", methods=["DELETE"])
def delete_candidate(candidate_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM candidates WHERE candidate_id = %s",
            (candidate_id,)
        )

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "message": "Candidate not found."
            }), 404

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Candidate deleted successfully."
        })

    except IntegrityError:
        if connection:
            connection.rollback()

        return jsonify({
            "success": False,
            "message": "Cannot delete candidate because linked application records exist."
        }), 409

    except Error:
        if connection:
            connection.rollback()

        return jsonify({
            "success": False,
            "message": "Database error while deleting candidate."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ---------------- COMPANY MANAGEMENT API ----------------

@app.route("/api/companies", methods=["GET"])
def api_get_companies():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                c.*,
                (
                    SELECT COUNT(*)
                    FROM jobs j
                    WHERE j.company_id = c.company_id
                    AND j.job_status = 'Open'
                ) AS open_jobs
            FROM companies c
            ORDER BY c.company_id DESC
        """)

        companies = cursor.fetchall()

        return jsonify({
            "success": True,
            "count": len(companies),
            "companies": companies
        })

    except Error:
        return jsonify({
            "success": False,
            "message": "Unable to load companies."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route("/api/companies", methods=["POST"])
def api_add_company():
    if not request.is_json:
        return jsonify({
            "success": False,
            "message": "JSON data is required."
        }), 415

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid company data."
        }), 400

    company_name = data.get("company_name")

    if not isinstance(company_name, str) or not company_name.strip():
        return jsonify({
            "success": False,
            "message": "Company name is required."
        }), 400

    company = Company(
        company_name=company_name.strip(),
        contact_person=str(data.get("contact_person") or "").strip(),
        email=str(data.get("email") or "").strip(),
        mobile=str(data.get("mobile") or "").strip(),
        location=str(data.get("location") or "").strip()
    )

    try:
        company_id = add_company(company)

        return jsonify({
            "success": True,
            "message": "Company added successfully!",
            "company_id": company_id
        }), 201

    except ValueError as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 400

    except IntegrityError:
        return jsonify({
            "success": False,
            "message": "Company email already exists or conflicts with database records."
        }), 409

    except Error:
        return jsonify({
            "success": False,
            "message": "Database error while adding company."
        }), 500


@app.route("/api/companies/<int:company_id>", methods=["GET"])
def api_get_company(company_id):
    try:
        company = get_company(company_id)

        if not company:
            return jsonify({
                "success": False,
                "message": "Company not found."
            }), 404

        return jsonify({
            "success": True,
            "company": company
        })

    except Error:
        return jsonify({
            "success": False,
            "message": "Unable to retrieve company."
        }), 500


@app.route("/api/companies/<int:company_id>", methods=["PUT"])
def api_update_company(company_id):
    if not request.is_json:
        return jsonify({
            "success": False,
            "message": "JSON data is required."
        }), 415

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid company data."
        }), 400

    company_name = data.get("company_name")

    if not isinstance(company_name, str) or not company_name.strip():
        return jsonify({
            "success": False,
            "message": "Company name is required."
        }), 400

    company = Company(
        company_name=company_name.strip(),
        contact_person=str(data.get("contact_person") or "").strip(),
        email=str(data.get("email") or "").strip(),
        mobile=str(data.get("mobile") or "").strip(),
        location=str(data.get("location") or "").strip()
    )

    try:
        updated = update_company(company_id, company)

        if not updated:
            return jsonify({
                "success": False,
                "message": "Company not found."
            }), 404

        return jsonify({
            "success": True,
            "message": "Company updated successfully."
        })

    except ValueError as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 400

    except IntegrityError:
        return jsonify({
            "success": False,
            "message": "Company email already exists."
        }), 409

    except Error:
        return jsonify({
            "success": False,
            "message": "Database error while updating company."
        }), 500


@app.route("/api/companies/<int:company_id>", methods=["DELETE"])
def api_delete_company(company_id):
    try:
        deleted = delete_company(company_id)

        if not deleted:
            return jsonify({
                "success": False,
                "message": "Company not found."
            }), 404

        return jsonify({
            "success": True,
            "message": "Company deleted successfully."
        })

    except ValueError as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 409

    except Error:
        return jsonify({
            "success": False,
            "message": "Database error while deleting company."
        }), 500

# ==========================================
# JOB MANAGEMENT API
# ==========================================

def build_job_from_data(data):
    if not isinstance(data, dict):
        raise ValueError("Invalid job data.")

    try:
        company_id = int(data.get("company_id"))
        openings = int(data.get("openings"))

        minimum_percentage = float(
            data.get("minimum_percentage") or 0
        )

        passing_year = data.get("passing_year")
        passing_year = int(passing_year) if passing_year not in (None, "") else None

        max_backlogs = int(data.get("max_backlogs") or 0)

        min_package = data.get("min_package")
        min_package = float(min_package) if min_package not in (None, "") else None

        max_package = data.get("max_package")
        max_package = float(max_package) if max_package not in (None, "") else None

    except (TypeError, ValueError):
        raise ValueError("Please enter valid numeric job details.")

    posted_date = str(data.get("posted_date") or date.today().isoformat())
    deadline = str(data.get("deadline") or "").strip() or None

    try:
        date.fromisoformat(posted_date)
        if deadline:
            date.fromisoformat(deadline)
    except ValueError:
        raise ValueError("Enter dates in YYYY-MM-DD format.")

    return Job(
        company_id=company_id,
        job_title=str(data.get("job_title") or "").strip(),
        openings=openings,
        qualification_required=str(
            data.get("qualification_required") or ""
        ).strip(),
        minimum_percentage=minimum_percentage,
        passing_year=passing_year,
        technology=str(data.get("technology") or "").strip(),
        required_skills=str(data.get("required_skills") or "").strip(),
        max_backlogs=max_backlogs,
        min_package=min_package,
        max_package=max_package,
        posted_date=posted_date,
        deadline=deadline,
        job_status=str(data.get("job_status") or "Open").strip()
    )


# GET ALL JOBS
@app.route("/api/jobs", methods=["GET"])
def api_get_jobs():
    try:
        jobs = get_all_jobs()

        return jsonify({
            "success": True,
            "count": len(jobs),
            "jobs": [
                serialize_candidate(job) for job in jobs
            ]
        })

    except Error:
        return jsonify({
            "success": False,
            "message": "Unable to load jobs."
        }), 500


# ADD JOB
@app.route("/api/jobs", methods=["POST"])
def api_add_job():
    if not request.is_json:
        return jsonify({
            "success": False,
            "message": "JSON data is required."
        }), 415

    try:
        job = build_job_from_data(request.get_json())
        job_id = add_job(job)

        return jsonify({
            "success": True,
            "message": "Job added successfully!",
            "job_id": job_id
        }), 201

    except ValueError as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 400

    except Error:
        return jsonify({
            "success": False,
            "message": "Database error while adding job."
        }), 500


# GET SINGLE JOB
@app.route("/api/jobs/<int:job_id>", methods=["GET"])
def api_get_job(job_id):
    try:
        job = get_job(job_id)

        if not job:
            return jsonify({
                "success": False,
                "message": "Job not found."
            }), 404

        return jsonify({
            "success": True,
            "job": serialize_candidate(job)
        })

    except Error:
        return jsonify({
            "success": False,
            "message": "Unable to retrieve job."
        }), 500


# UPDATE JOB
@app.route("/api/jobs/<int:job_id>", methods=["PUT"])
def api_update_job(job_id):
    if not request.is_json:
        return jsonify({
            "success": False,
            "message": "JSON data is required."
        }), 415

    try:
        job = build_job_from_data(request.get_json())

        existing_job = get_job(job_id)

        if not existing_job:
            return jsonify({
                "success": False,
                "message": "Job not found."
            }), 404

        update_job(job_id, job)

        return jsonify({
            "success": True,
            "message": "Job updated successfully."
        })

    except ValueError as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 400

    except Error:
        return jsonify({
            "success": False,
            "message": "Database error while updating job."
        }), 500


# DELETE JOB
@app.route("/api/jobs/<int:job_id>", methods=["DELETE"])
def api_delete_job(job_id):
    try:
        deleted = delete_job(job_id)

        if not deleted:
            return jsonify({
                "success": False,
                "message": "Job not found."
            }), 404

        return jsonify({
            "success": True,
            "message": "Job deleted successfully."
        })

    except ValueError as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 409

    except Error:
        return jsonify({
            "success": False,
            "message": "Database error while deleting job."
        }), 500

    
# ---------------- APPLICATION API ----------------

@app.route("/api/applications", methods=["GET"])
def api_get_applications():
    try:
        applications = get_all_applications()

        return jsonify({
            "success": True,
            "count": len(applications),
            "applications": [
                serialize_candidate(application)
                for application in applications
            ]
        })

    except Error:
        return jsonify({
            "success": False,
            "message": "Database error while fetching applications."
        }), 500


@app.route("/api/applications", methods=["POST"])
def api_add_application():
    try:
        data = request.get_json(silent=True) or {}

        candidate_id = int(data.get("candidate_id", 0))
        job_id = int(data.get("job_id", 0))

        if candidate_id <= 0 or job_id <= 0:
            return jsonify({
                "success": False,
                "message": "Valid candidate ID and job ID are required."
            }), 400

        application = Application(
            candidate_id=candidate_id,
            job_id=job_id,
            application_status="Applied"
        )

        application_id = add_application(application)

        return jsonify({
            "success": True,
            "message": "Application submitted successfully.",
            "application_id": application_id
        }), 201

    except (ValueError, TypeError) as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 400

    except Error:
        return jsonify({
            "success": False,
            "message": "Database error while submitting application."
        }), 500


@app.route("/api/applications/<int:application_id>", methods=["PUT"])
def api_update_application(application_id):
    try:
        data = request.get_json(silent=True) or {}
        new_status = data.get("application_status", "")

        updated = update_application_status(
            application_id,
            new_status
        )

        if not updated:
            return jsonify({
                "success": False,
                "message": "Application not found."
            }), 404

        return jsonify({
            "success": True,
            "message": "Application status updated successfully."
        })

    except ValueError as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 400

    except Error:
        return jsonify({
            "success": False,
            "message": "Database error while updating application."
        }), 500


@app.route("/api/applications/<int:application_id>", methods=["DELETE"])
def api_delete_application(application_id):
    try:
        deleted = delete_application(application_id)

        if not deleted:
            return jsonify({
                "success": False,
                "message": "Application not found."
            }), 404

        return jsonify({
            "success": True,
            "message": "Application deleted successfully."
        })

    except ValueError as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 409

    except Error:
        return jsonify({
            "success": False,
            "message": "Database error while deleting application."
        }), 500

# ---------------- INTERVIEW API ----------------

@app.route("/api/interviews", methods=["GET"])
def api_get_interviews():
    try:
        interviews = get_all_interviews()
        return jsonify({
            "success": True,
            "count": len(interviews),
            "interviews": [
                serialize_candidate(interview)
                for interview in interviews
            ]
        })
    except Error:
        return jsonify({
            "success": False,
            "message": "Database error while fetching interviews."
        }), 500


@app.route("/api/interviews", methods=["POST"])
def api_add_interview():
    try:
        data = request.get_json(silent=True) or {}

        application_id = int(data.get("application_id", 0))
        if application_id <= 0:
            return jsonify({
                "success": False,
                "message": "Valid application ID is required."
            }), 400

        interview = Interview(
            application_id=application_id,
            round_name=str(data.get("round_name", "")).strip(),
            interview_date=data.get("interview_date", ""),
            interviewer=str(data.get("interviewer", "")).strip(),
            feedback=str(data.get("feedback", "")).strip(),
            result=data.get("result", "Pending")
        )

        interview_id = schedule_interview(interview)

        return jsonify({
            "success": True,
            "message": "Interview scheduled successfully.",
            "interview_id": interview_id
        }), 201

    except (ValueError, TypeError) as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 400
    except Error:
        return jsonify({
            "success": False,
            "message": "Database error while scheduling interview."
        }), 500


@app.route("/api/interviews/<int:interview_id>", methods=["GET"])
def api_get_interview(interview_id):
    try:
        interview = get_interview(interview_id)

        if not interview:
            return jsonify({
                "success": False,
                "message": "Interview not found."
            }), 404

        return jsonify({
            "success": True,
            "interview": serialize_candidate(interview)
        })

    except Error:
        return jsonify({
            "success": False,
            "message": "Database error."
        }), 500


@app.route("/api/interviews/<int:interview_id>", methods=["PUT"])
def api_update_interview(interview_id):
    try:
        data = request.get_json(silent=True) or {}

        interview = Interview(
            application_id=int(data.get("application_id", 0)),
            round_name=str(data.get("round_name", "")).strip(),
            interview_date=data.get("interview_date", ""),
            interviewer=str(data.get("interviewer", "")).strip(),
            feedback=str(data.get("feedback", "")).strip(),
            result=data.get("result", "Pending")
        )

        updated = update_interview(interview_id, interview)

        if not updated:
            return jsonify({
                "success": False,
                "message": "Interview not found."
            }), 404

        return jsonify({
            "success": True,
            "message": "Interview updated successfully."
        })

    except (ValueError, TypeError) as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 400
    except Error:
        return jsonify({
            "success": False,
            "message": "Database error while updating interview."
        }), 500


@app.route("/api/interviews/<int:interview_id>/result", methods=["PUT"])
def api_update_interview_result(interview_id):
    try:
        data = request.get_json(silent=True) or {}
        new_result = data.get("result", "")

        updated = update_interview_result(interview_id, new_result)

        if not updated:
            return jsonify({
                "success": False,
                "message": "Interview not found."
            }), 404

        return jsonify({
            "success": True,
            "message": "Interview result updated successfully."
        })

    except ValueError as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 400
    except Error:
        return jsonify({
            "success": False,
            "message": "Database error."
        }), 500


@app.route("/api/interviews/<int:interview_id>", methods=["DELETE"])
def api_delete_interview(interview_id):
    try:
        deleted = delete_interview(interview_id)

        if not deleted:
            return jsonify({
                "success": False,
                "message": "Interview not found."
            }), 404

        return jsonify({
            "success": True,
            "message": "Interview deleted successfully."
        })

    except Error:
        return jsonify({
            "success": False,
            "message": "Database error while deleting interview."
        }), 500

# ---------------- OFFER API ROUTES ----------------

@app.route("/api/offers", methods=["GET"])
def api_get_offers():
    try:
        offers = get_all_offers()
        return jsonify({
            "success": True,
            "count": len(offers),
            "offers": [
                offer.__dict__ if hasattr(offer, "__dict__") else offer
                for offer in offers
            ]
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/offers", methods=["POST"])
def api_add_offer():
    try:
        data = request.get_json()

        offer = Offer(
            application_id=int(data["application_id"]),
            offer_date=data.get("offer_date"),
            package=float(data["package"]),
            offer_status=data.get("offer_status", "Pending"),
            joining_date=data.get("joining_date")
        )

        result = add_offer(offer)

        return jsonify({
            "success": True,
            "message": "Offer added successfully",
            "result": result
        }), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/api/offers/<int:offer_id>", methods=["GET"])
def api_get_offer(offer_id):
    try:
        offer = get_offer(offer_id)

        if not offer:
            return jsonify({
                "success": False,
                "message": "Offer not found"
            }), 404

        return jsonify({
            "success": True,
            "offer": offer.__dict__ if hasattr(offer, "__dict__") else offer
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/offers/<int:offer_id>", methods=["PUT"])
def api_update_offer(offer_id):
    try:
        data = request.get_json()

        offer = Offer(
            application_id=int(data["application_id"]),
            offer_date=data.get("offer_date"),
            package=float(data["package"]),
            offer_status=data.get("offer_status", "Pending"),
            joining_date=data.get("joining_date")
        )

        update_offer(offer_id, offer)

        return jsonify({
            "success": True,
            "message": "Offer updated successfully"
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/api/offers/<int:offer_id>/status", methods=["PUT"])
def api_update_offer_status(offer_id):
    try:
        data = request.get_json()
        update_offer_status(
            offer_id,
            data["offer_status"]
        )

        return jsonify({
            "success": True,
            "message": "Offer status updated successfully"
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/api/offers/<int:offer_id>", methods=["DELETE"])
def api_delete_offer(offer_id):
    try:
        delete_offer(offer_id)

        return jsonify({
            "success": True,
            "message": "Offer deleted successfully"
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# ---------------- PLACEMENT API ROUTES ----------------

@app.route("/api/placements", methods=["GET"])
def api_get_placements():
    try:
        placements = get_all_placements()

        return jsonify({
            "success": True,
            "count": len(placements),
            "placements": [
                {
                    key: (
                        value.isoformat()
                        if hasattr(value, "isoformat")
                        else float(value)
                        if isinstance(value, Decimal)
                        else value
                    )
                    for key, value in placement.items()
                }
                for placement in placements
            ]
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/placements", methods=["POST"])
def api_add_placement():
    try:
        data = request.get_json()

        placement = Placement(
            candidate_id=int(data["candidate_id"]),
            company_id=int(data["company_id"]),
            job_id=int(data["job_id"]),
            joining_date=data.get("joining_date"),
            package=float(data["package"]),
            placement_status=data.get("placement_status", "Confirmed")
        )

        placement_id = add_placement(placement)

        return jsonify({
            "success": True,
            "message": "Placement added successfully",
            "placement_id": placement_id
        }), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/api/placements/<int:placement_id>", methods=["GET"])
def api_get_placement(placement_id):
    try:
        placement = get_placement(placement_id)

        if not placement:
            return jsonify({"success": False, "message": "Placement not found"}), 404

        return jsonify({
            "success": True,
            "placement": {
                key: (
                    value.isoformat()
                    if hasattr(value, "isoformat")
                    else float(value)
                    if isinstance(value, Decimal)
                    else value
                )
                for key, value in placement.items()
            }
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/placements/<int:placement_id>", methods=["PUT"])
def api_update_placement(placement_id):
    try:
        data = request.get_json()

        placement = Placement(
            candidate_id=int(data["candidate_id"]),
            company_id=int(data["company_id"]),
            job_id=int(data["job_id"]),
            joining_date=data.get("joining_date"),
            package=float(data["package"]),
            placement_status=data.get("placement_status", "Confirmed")
        )

        updated = update_placement(placement_id, placement)

        if not updated:
            return jsonify({"success": False, "message": "Placement not found"}), 404

        return jsonify({"success": True, "message": "Placement updated successfully"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/api/placements/<int:placement_id>", methods=["DELETE"])
def api_delete_placement(placement_id):
    try:
        deleted = delete_placement(placement_id)

        if not deleted:
            return jsonify({"success": False, "message": "Placement not found"}), 404

        return jsonify({"success": True, "message": "Placement deleted successfully"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

    
# ---------------- REPORTS API ----------------

@app.route("/api/reports", methods=["GET"])
def api_reports():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        queries = {
            "total_candidates": "SELECT COUNT(*) AS total FROM candidates",
            "total_companies": "SELECT COUNT(*) AS total FROM companies",
            "total_jobs": "SELECT COUNT(*) AS total FROM jobs",
            "total_applications": "SELECT COUNT(*) AS total FROM applications",
            "applied": "SELECT COUNT(*) AS total FROM applications WHERE application_status = 'Applied'",
            "shortlisted": "SELECT COUNT(*) AS total FROM applications WHERE application_status = 'Shortlisted'",
            "selected": "SELECT COUNT(*) AS total FROM applications WHERE application_status = 'Selected'",
            "total_interviews": "SELECT COUNT(*) AS total FROM interviews",
            "interviewed": "SELECT COUNT(DISTINCT application_id) AS total FROM interviews",
            "total_offers": "SELECT COUNT(*) AS total FROM offers",
            "open_jobs": "SELECT COUNT(*) AS total FROM jobs WHERE job_status = 'Open'",
            "accepted_offers": "SELECT COUNT(*) AS total FROM offers WHERE offer_status = 'Accepted'",
            "total_placements": "SELECT COUNT(*) AS total FROM placements WHERE placement_status != 'Cancelled'",
            "joined": "SELECT COUNT(*) AS total FROM placements WHERE placement_status = 'Joined'",
            
        }

        report = {}

        for key, query in queries.items():
            cursor.execute(query)
            result = cursor.fetchone()
            report[key] = result["total"]

        if report["total_candidates"] > 0:
            report["placement_rate"] = round(
                (report["total_placements"] / report["total_candidates"]) * 100, 2
            )
        else:
            report["placement_rate"] = 0

        return jsonify({
            "success": True,
            "report": report
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

            
# ---------------- AI RESUME SCREENING API ----------------

@app.route("/api/resume-screening", methods=["POST"])
def screen_resume():

    try:
        candidate_id = request.form.get("candidate_id", type=int)
        job_id = request.form.get("job_id", type=int)
        resume = request.files.get("resume")

        if not candidate_id or not job_id:
            return jsonify({
                "success": False,
                "message": "Candidate ID and Job ID are required."
            }), 400

        if not resume or not resume.filename:
            return jsonify({
                "success": False,
                "message": "Please upload a resume."
            }), 400

        if not allowed_resume_file(resume.filename):
            return jsonify({
                "success": False,
                "message": "Only PDF and DOCX files are allowed."
            }), 400

        filename = secure_filename(resume.filename)

        if not filename:
            return jsonify({
                "success": False,
                "message": "Invalid filename."
            }), 400

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT candidate_id FROM candidates WHERE candidate_id = %s",
                (candidate_id,)
            )
            candidate = cursor.fetchone()

            cursor.execute(
                "SELECT job_id, required_skills FROM jobs WHERE job_id = %s",
                (job_id,)
            )
            job = cursor.fetchone()

        finally:
            cursor.close()
            connection.close()

        if not candidate or not job:
            return jsonify({
                "success": False,
                "message": "Candidate or Job not found."
            }), 404

        saved_path = Path(app.config["UPLOAD_FOLDER"]) / filename

        if saved_path.exists():
            filename = f"{Path(filename).stem}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}{Path(filename).suffix}"
            saved_path = Path(app.config["UPLOAD_FOLDER"]) / filename

        resume.save(str(saved_path))

        try:
            resume_text = extract_resume_text(saved_path)

            if not resume_text:
                saved_path.unlink(missing_ok=True)
                return jsonify({
                    "success": False,
                    "message": "No readable text found in resume."
                }), 400

            candidate_skills = extract_skills(resume_text)

            required_skills = [
                skill.strip()
                for skill in (job["required_skills"] or "").split(",")
                if skill.strip()
            ]

            matching_score = calculate_match_score(
                candidate_skills,
                required_skills
            )

            screening_id = ResumeScreening.add_screening(
                candidate_id,
                job_id,
                filename,
                candidate_skills,
                matching_score
            )

            return jsonify({
                "success": True,
                "message": "Resume screened successfully.",
                "screening_id": screening_id,
                "candidate_skills": candidate_skills,
                "required_skills": required_skills,
                "matching_score": matching_score
            }), 201

        except Exception:
            saved_path.unlink(missing_ok=True)
            raise

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route("/api/resume-screenings", methods=["GET"])
def get_resume_screenings():

    try:
        screenings = ResumeScreening.get_all_screenings()

        return jsonify({
            "success": True,
            "count": len(screenings),
            "screenings": screenings
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ---------------- START SERVER ----------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )

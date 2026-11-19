# RecruitIQ – Intelligent Recruitment & Placement Management System

## Project Overview
RecruitIQ is a Python-based Recruitment and Placement Management System developed using Flask, MySQL, HTML, CSS and JavaScript.

It helps placement officers manage candidates, companies, job openings, applications, interviews, offers, placements and resume screening through a centralized desktop application.

## Main Features
- Admin Login and Logout
- Candidate Management
- Company Management
- Job Management
- Application Management
- Interview Scheduling and Management
- Offer Management
- Placement Management
- Candidate Eligibility Verification
- Resume Screening with keyword-based skill matching
- Recruitment and Placement Reports
- Dashboard with charts
- Windows Desktop Application (.exe)

## Technologies Used
- Python
- Flask
- MySQL
- HTML5
- CSS3
- JavaScript
- PyWebView
- PyInstaller

## Project Structure
- `app.py` – Flask application and API routes
- `desktop_app.py` – Desktop application launcher
- `database.py` – MySQL connection
- `config.py` – Environment configuration
- `database/` – Database schema
- `frontend/` – HTML, CSS and JavaScript pages
- `models/` – Database models
- `services/` – Business logic
- `utils/` – Utility modules
- `uploads/` – Uploaded resumes
- `requirements.txt` – Python dependencies
- `dist/RecruitIQ/` – Desktop application build

## Installation and Setup

1. Install Python and MySQL Server.
2. Open the project folder in VS Code.
3. Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

4. Install dependencies:

```powershell
pip install -r requirements.txt
```

5. Configure your MySQL credentials in `.env`.
6. Create the database `recruitment_placement`.
7. Execute `database/schema.sql` in MySQL.
8. Start the web application:

```powershell
python app.py
```

9. Open the browser:

`http://127.0.0.1:5000`

## Desktop Application

Run the desktop application using:

```powershell
python desktop_app.py
```

Or open the built application:

`dist/RecruitIQ/RecruitIQ.exe`

Keep the complete `RecruitIQ` distribution folder, including `_internal`.

MySQL Server must be running and the database must be configured.

## Demo Admin Login

- Email: `admin@example.com`
- Password: `admin123`

These are demo credentials. Change them before production use.

## Resume Screening
The resume screening feature extracts resume text and compares candidate skills with job-required skills using keyword matching.

## Project Purpose
This project is developed for academic purposes to demonstrate recruitment and placement management using Python, Flask and MySQL.

## Developer
Developed as a BCA academic project.

CREATE DATABASE IF NOT EXISTS recruitment_placement;
USE recruitment_placement;

CREATE TABLE IF NOT EXISTS candidates (
    candidate_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    mobile VARCHAR(10) NOT NULL,
    qualification VARCHAR(100),
    percentage DECIMAL(5,2),
    passing_year YEAR,
    technology VARCHAR(100),
    skills TEXT,
    backlogs INT NOT NULL DEFAULT 0,
    candidate_status ENUM('Active','Inactive','Placed') NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(120),
    email VARCHAR(150),
    mobile VARCHAR(10),
    location VARCHAR(150),
    company_status ENUM('Active','Inactive') NOT NULL DEFAULT 'Active'
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    job_title VARCHAR(150) NOT NULL,
    qualification_required VARCHAR(100),
    minimum_percentage DECIMAL(5,2) DEFAULT 0,
    passing_year INT,
    technology VARCHAR(100),
    required_skills TEXT,
    max_backlogs INT DEFAULT 0,
    openings INT NOT NULL,
    min_package DECIMAL(10,2),
    max_package DECIMAL(10,2),
    posted_date DATE,
    deadline DATE,
    job_status ENUM('Open','Closed','On Hold') NOT NULL DEFAULT 'Open',
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    job_id INT NOT NULL,
    application_date DATE NOT NULL,
    application_status ENUM('Applied','Shortlisted','Rejected','Selected','Withdrawn') DEFAULT 'Applied',
    UNIQUE KEY unique_candidate_job (candidate_id, job_id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id),
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);

CREATE TABLE IF NOT EXISTS interviews (
    interview_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    round_name VARCHAR(100) NOT NULL,
    interview_date DATETIME NOT NULL,
    interviewer VARCHAR(120),
    feedback TEXT,
    result ENUM('Pending','Selected','Rejected','Next Round') DEFAULT 'Pending',
    FOREIGN KEY (application_id) REFERENCES applications(application_id)
);

CREATE TABLE IF NOT EXISTS offers (
    offer_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    offer_date DATE,
    package DECIMAL(10,2),
    offer_status ENUM('Pending','Accepted','Declined') DEFAULT 'Pending',
    joining_date DATE,
    FOREIGN KEY (application_id) REFERENCES applications(application_id)
);

CREATE TABLE IF NOT EXISTS placements (
    placement_id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    company_id INT NOT NULL,
    job_id INT NOT NULL,
    joining_date DATE,
    package DECIMAL(10,2),
    placement_status ENUM('Confirmed','Joined','Cancelled') DEFAULT 'Confirmed',
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);


import re


KNOWN_SKILLS = [
    "Python",
    "Java",
    "C",
    "C++",
    "Django",
    "Flask",
    "Django REST Framework",
    "HTML",
    "CSS",
    "JavaScript",
    "React",
    "SQL",
    "MySQL",
    "SQLite",
    "MongoDB",
    "Oracle",
    "PostgreSQL",
    "Machine Learning",
    "Artificial Intelligence",
    "Data Analysis",
    "Pandas",
    "NumPy",
    "Matplotlib",
    "Power BI",
    "Excel",
    "Git",
    "GitHub",
    "REST API",
    "OOP",
    "Data Structures",
    "Algorithms",
    "AWS",
    "Linux"
]


def extract_skills(resume_text):
    if not resume_text:
        return []

    text = resume_text.lower()
    found_skills = []

    for skill in KNOWN_SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"

        if re.search(pattern, text):
            found_skills.append(skill)

    return found_skills

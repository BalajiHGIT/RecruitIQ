
from database import get_connection


class ResumeScreening:

    @staticmethod
    def add_screening(candidate_id, job_id, resume_filename,
                      extracted_skills, matching_score):

        conn = get_connection()
        cursor = conn.cursor()

        try:
            query = """
                INSERT INTO resume_screenings
                (candidate_id, job_id, resume_filename,
                 extracted_skills, matching_score)
                VALUES (%s, %s, %s, %s, %s)
            """

            skills_text = ", ".join(extracted_skills)

            cursor.execute(
                query,
                (
                    candidate_id,
                    job_id,
                    resume_filename,
                    skills_text,
                    matching_score
                )
            )

            conn.commit()
            return cursor.lastrowid

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_all_screenings():

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT rs.*, c.full_name, j.job_title
                FROM resume_screenings rs
                JOIN candidates c
                    ON rs.candidate_id = c.candidate_id
                JOIN jobs j
                    ON rs.job_id = j.job_id
                ORDER BY rs.screening_date DESC
            """)

            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()

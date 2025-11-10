from typing import Optional, List, Dict
from datetime import date
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection as _PGConn


def getAllStudents(conn: _PGConn) -> List[Dict]:
    """
    Gets all students from the database. Returns a list of dictionaries with their info.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT student_id, first_name, last_name, email, enrollment_date
            FROM public.students
            ORDER BY student_id;
        """)
        return [dict(r) for r in cur.fetchall()]


def addStudent(conn: _PGConn, first_name: str, last_name: str, email: str,
               enrollment_date: Optional[date]) -> int:
    """
    Adds a new student to the database. Returns their new student_id.
    Will throw an error if the email already exists.
    """
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO public.students (first_name, last_name, email, enrollment_date)
                VALUES (%s, %s, %s, %s)
                RETURNING student_id;
            """, (first_name, last_name, email, enrollment_date))
            return cur.fetchone()[0]


def updateStudentEmail(conn: _PGConn, student_id: int, new_email: str) -> int:
    """
    Updates a student's email address. Returns how many rows were updated (0 means the student wasn't found).
    """
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE public.students
                SET email = %s
                WHERE student_id = %s;
            """, (new_email, student_id))
            return cur.rowcount


def deleteStudent(conn: _PGConn, student_id: int) -> int:
    """
    Deletes a student by their ID. Returns how many rows were deleted (0 if they don't exist).
    """
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM public.students
                WHERE student_id = %s;
            """, (student_id,))
            return cur.rowcount

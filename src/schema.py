from psycopg2.extensions import connection as _PGConn

def ensure_table_and_seed(conn: _PGConn) -> None:
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS public.students (
                    student_id SERIAL PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    enrollment_date DATE
                );
            """)

            # Initial seed data
            cur.execute("""
                INSERT INTO public.students
                    (first_name, last_name, email, enrollment_date)
                VALUES
                    ('John','Doe','john.doe@example.com','2023-09-01'),
                    ('Jane','Smith','jane.smith@example.com','2023-09-01'),
                    ('Jim','Beam','jim.beam@example.com','2023-09-02')
                ON CONFLICT (email) DO NOTHING;
            """)

def reset_to_seed(conn) -> None:
    """
    Wipes the students table and puts back the original 3 test records. FOR TESTING PURPOSES
    """
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                TRUNCATE TABLE public.students RESTART IDENTITY CASCADE;
            """)
            cur.execute("""
                INSERT INTO public.students (first_name, last_name, email, enrollment_date) VALUES
                ('John','Doe','john.doe@example.com','2023-09-01'),
                ('Jane','Smith','jane.smith@example.com','2023-09-01'),
                ('Jim','Beam','jim.beam@example.com','2023-09-02');
            """)


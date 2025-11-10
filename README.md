# COMP 3005A - Database Management Systems

Assignment 3 Question 1

Afaq Virk

Install necessary dependencies:

```bash
pip install psycopg2-binary python-dotenv
```

Create a `.env` in the project root (you may chnage the template extension):

```ini
PGHOST=localhost
PGPORT=5432
PGDATABASE=school_db
PGUSER=postgres
PGPASSWORD=your_password_here
```

and run

```bash
python app.py shell
```

or

```bash
python app.py demo
```

And follow the prompts provided.

Shell examples

```
students> getAllStudents()
students> addStudent("John","Doe","john.doe2@example.com","2023-09-10")
students> updateStudentEmail(4,"john.doe2@school.edu")
students> deleteStudent(4)
students> quit
```

Video demo: https://www.youtube.com/watch?v=GJ_f1ptJb1s

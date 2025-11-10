"""
Main entry point for the students database app
Run with 'shell' mode (default) for interactive use, or 'demo' to see a quick walkthrough
"""

import argparse
import sys
import os
import time
from datetime import date
import psycopg2

from src.config import ensure_database_exists, get_connection
from src.schema import ensure_table_and_seed
from src.students import getAllStudents, addStudent, updateStudentEmail, deleteStudent
from src.shell import StudentFuncShell

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_students(conn, label: str):
    print(f"\n=== {label} ===")
    for row in getAllStudents(conn):
        print(f"{row['student_id']:>2} | {row['first_name']} {row['last_name']} | {row['email']} | {row['enrollment_date']}")

def run_demo(conn):
    """DEMO for video use only"""

    clear_screen()
    # READ
    print_students(conn, "Initial students")
    time.sleep(2)
    
    # CREATE
    print("\nAdding a new student...")
    new_id = addStudent(conn, "Afaq", "Virk", "afaq.virk@example.com", date.fromisoformat("2023-09-03"))
    print(f"Added student_id = {new_id}")
    print_students(conn, "After add")
    time.sleep(2)

    # UPDATE
    print("\nUpdating Afaq's email...")
    rows = updateStudentEmail(conn, new_id, "afaq.virk@example.edu")
    print(f"Rows updated = {rows}")
    print_students(conn, "After update")
    time.sleep(2)

    #DELETE
    print("\nDeleting Afaq...")
    rows = deleteStudent(conn, new_id)
    print(f"Rows deleted = {rows}")
    print_students(conn, "After delete")
    time.sleep(1)
    print("\nDemo complete")

def main():
    parser = argparse.ArgumentParser(description="Students CRUD (PostgreSQL + Python)")
    parser.add_argument("mode", nargs="?", choices=["shell","demo"], default="shell")
    args = parser.parse_args()

    try:
        ensure_database_exists()
        conn = get_connection()
        ensure_table_and_seed(conn)

        if args.mode == "demo":
            run_demo(conn)
        else:
            StudentFuncShell(conn).cmdloop()

    except psycopg2.Error as e:
        print("Database error:", e.pgerror or str(e))
        sys.exit(1)
    except Exception as e:
        print("Error:", str(e))
        sys.exit(1)

if __name__ == "__main__": 
    main()

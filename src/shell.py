import cmd
import re
import ast
from datetime import date
from typing import Any, List

from psycopg2.extensions import connection as _PGConn
from .students import (
    getAllStudents as _getAllStudents,
    addStudent as _addStudent,
    updateStudentEmail as _updateStudentEmail,
    deleteStudent as _deleteStudent,
)
from .schema import reset_to_seed

_CALL_RE = re.compile(r"^\s*([A-Za-z_]\w*)\s*\((.*)\)\s*$")


def _parse_args(args_text: str) -> List[Any]:
    """
    Parses function arguments from a string. Handles things like:
      '' -> []
      '"John", "Doe", 3' -> ["John","Doe",3]
      '"2023-09-01"' -> ["2023-09-01"]
    """
    if args_text.strip() == "":
        return []
    try:
        node = ast.parse(f"f({args_text})", mode="eval")
        if not hasattr(node.body, "args"):
            raise ValueError("Invalid argument list")
        return [ast.literal_eval(a) for a in node.body.args]
    except Exception as e:
        raise ValueError(f"Could not parse arguments: {e}")


def _maybe_parse_date(s: Any) -> Any:
    """
    If the string looks like a date (YYYY-MM-DD), convert it to a date object.
    Otherwise just return whatever was passed in.
    """
    if isinstance(s, str):
        s_strip = s.strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s_strip):
            try:
                return date.fromisoformat(s_strip)
            except ValueError:
                pass
    return s


class StudentFuncShell(cmd.Cmd):
    intro = (
        "Function-call shell. Examples:\n"
        "  getAllStudents()\n"
        '  addStudent("John","Doe","john.doe@example.com","2023-09-01")\n'
        '  updateStudentEmail(12,"john.doe@school.edu")\n'
        "  deleteStudent(12)\n"
        "Type 'help' for more details. Type 'exit' or 'quit' to leave."
    )
    prompt = "students> "

    def __init__(self, conn: _PGConn):
        super().__init__()
        self.conn = conn

    def default(self, line: str):
        """
        Handles function calls that don't match built-in commands.
        Expects stuff like: funcName(arg1, arg2, ...)
        """
        m = _CALL_RE.match(line)
        if not m:
            print("*** Unknown syntax:", line)
            return

        func_name, args_text = m.group(1), m.group(2)
        try:
            args = _parse_args(args_text)
        except ValueError as e:
            print("Error:", e)
            return

        # dispatcher
        try:
            if func_name == "getAllStudents":
                self._cmd_getAllStudents(args)
            elif func_name == "addStudent":
                self._cmd_addStudent(args)
            elif func_name == "updateStudentEmail":
                self._cmd_updateStudentEmail(args)
            elif func_name == "deleteStudent":
                self._cmd_deleteStudent(args)
            elif func_name == "resetToSeed":
                self._cmd_resetToSeed(args)
            else:
                print(f"*** Unknown function: {func_name}")
        except Exception as e:
            print("Error:", e)

    def emptyline(self):
        pass

    def do_exit(self, arg):
        "Quits the shell."
        print("Bye!")
        return True

    def do_quit(self, arg):
        "Same as exit."
        return self.do_exit(arg)

    def do_help(self, arg):
        print(
            """
Accepted commands (exact names):

  getAllStudents()

  addStudent(first_name, last_name, email, enrollment_date)
    - Example:
      addStudent("Alice","Wong","alice.wong@example.com","2023-09-03")

  updateStudentEmail(student_id, new_email)
    - Example:
      updateStudentEmail(12,"alice.w@example.edu")

  deleteStudent(student_id)
    - Example:
      deleteStudent(12)

Notes:
- Strings must be quoted. Dates should be "YYYY-MM-DD".
- Whitespace is allowed. Case-sensitive function names.
- Use exit or quit to leave.
"""
        )

    def _cmd_getAllStudents(self, args):
        if len(args) != 0:
            print("Usage: getAllStudents()")
            return
        rows = _getAllStudents(self.conn)
        if not rows:
            print("(no rows)")
            return
        print(f"{'ID':>3} | {'First':<12} | {'Last':<12} | {'Email':<28} | Enrolled")
        print("-" * 75)
        for r in rows:
            print(
                f"{r['student_id']:>3} | {r['first_name']:<12} | {r['last_name']:<12} | "
                f"{r['email']:<28} | {r['enrollment_date']}"
            )

    def _cmd_addStudent(self, args):
        if not (3 <= len(args) <= 4):
            print('Usage: addStudent(first_name, last_name, email, enrollment_date)')
            return
        first, last, email = args[0], args[1], args[2]
        enroll = _maybe_parse_date(args[3]) if len(args) == 4 else None
        new_id = _addStudent(self.conn, str(first), str(last), str(email), enroll)
        print(f"Added student_id = {new_id}")

    def _cmd_updateStudentEmail(self, args):
        if len(args) != 2:
            print('Usage: updateStudentEmail(student_id, new_email)')
            return
        sid = int(args[0])
        new_email = str(args[1])
        updated = _updateStudentEmail(self.conn, sid, new_email)
        print(f"Rows updated = {updated}")

    def _cmd_deleteStudent(self, args):
        if len(args) != 1:
            print('Usage: deleteStudent(student_id)')
            return
        sid = int(args[0])
        deleted = _deleteStudent(self.conn, sid)
        print(f"Rows deleted = {deleted}")

    def _cmd_resetToSeed(self, args):
        if len(args) != 0:
            print("Usage: resetToSeed()")
            return
        reset_to_seed(self.conn)
        print("Students table reset to initial seed (John, Jane, Jim).")

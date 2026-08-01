"""
EduOS Student Roster
Student registry with enrollment-number validation.
Used to verify that exam submissions come from registered students.
"""

import csv
import json
import re
from pathlib import Path

# Matches typical Indian university enrollment numbers:
# e.g. "2021CSE045", "22BCS1234", "21MCA-015"
ROLL_RE = re.compile(r"^[0-9]{2,4}[A-Za-z]{2,6}[0-9]{2,6}$")
# Emails like name@college.edu
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

MIN_ENROLLMENT_LENGTH = 6
MAX_ENROLLMENT_LENGTH = 16


def validate_student_id(student_id: str) -> dict:
    """
    Validate a student ID / enrollment number.
    Returns a dict with 'valid' and a human-readable 'reason' on failure.
    """
    if not student_id or not isinstance(student_id, str):
        return {"valid": False, "reason": "student_id is required"}
    sid = student_id.strip()
    if not sid:
        return {"valid": False, "reason": "student_id is required"}
    if not (MIN_ENROLLMENT_LENGTH <= len(sid) <= MAX_ENROLLMENT_LENGTH):
        return {"valid": False,
                "reason": f"enrollment must be {MIN_ENROLLMENT_LENGTH}-"
                          f"{MAX_ENROLLMENT_LENGTH} characters"}
    if not ROLL_RE.match(sid):
        return {"valid": False,
                "reason": "enrollment format is invalid (expected e.g. "
                          "'2021CSE045' or '22BCS1234')"}
    return {"valid": True, "reason": ""}


class Roster:
    """Persistent student roster stored as JSON next to the module."""

    DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "roster.json"

    def __init__(self, path: Path = None):
        self.path = Path(path) if path else self.DEFAULT_PATH
        self._students = {}
        self.load()

    def load(self) -> None:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text())
                self._students = data if isinstance(data, dict) else {}
            except (json.JSONDecodeError, OSError):
                self._students = {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._students, indent=2))

    def add_student(self, student_id: str, name: str = "",
                    email: str = "", course: str = "") -> dict:
        """Add a student. Returns result dict with 'ok' and 'error'."""
        validation = validate_student_id(student_id)
        if not validation["valid"]:
            return {"ok": False, "error": validation["reason"]}
        if email and not EMAIL_RE.match(email):
            return {"ok": False, "error": "email format is invalid"}
        if student_id in self._students:
            return {"ok": False, "error": f"{student_id} already in roster"}
        self._students[student_id] = {
            "student_id": student_id,
            "name": name,
            "email": email,
            "course": course,
            "status": "active",
        }
        self.save()
        return {"ok": True, "student": self._students[student_id]}

    def remove_student(self, student_id: str) -> dict:
        if student_id not in self._students:
            return {"ok": False, "error": f"{student_id} not in roster"}
        del self._students[student_id]
        self.save()
        return {"ok": True}

    def is_registered(self, student_id: str) -> bool:
        sid = (student_id or "").strip()
        return sid in self._students

    def get_student(self, student_id: str) -> dict:
        sid = (student_id or "").strip()
        return self._students.get(sid)

    def all_students(self) -> list:
        return list(self._students.values())

    def count(self) -> int:
        return len(self._students)

    def import_csv(self, path: Path) -> dict:
        """Import students from CSV with columns: student_id,name,email,course."""
        added = skipped = 0
        errors = []
        with open(path, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                result = self.add_student(
                    row.get('student_id', '').strip(),
                    row.get('name', '').strip(),
                    row.get('email', '').strip(),
                    row.get('course', '').strip(),
                )
                if result["ok"]:
                    added += 1
                else:
                    skipped += 1
                    errors.append((row.get('student_id', ''), result["error"]))
        return {"added": added, "skipped": skipped, "errors": errors}

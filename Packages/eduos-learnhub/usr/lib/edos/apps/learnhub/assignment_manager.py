import json
from datetime import datetime

class AssignmentManager:
    def __init__(self):
        self.assignments = {}

    def create_assignment(self, aid, title, description, due_date, course_id):
        self.assignments[aid] = {
            "id": aid, "title": title, "description": description,
            "due_date": due_date, "course_id": course_id,
            "submitted": False, "grade": None,
            "created": datetime.now().isoformat()
        }
        return True

    def submit_assignment(self, aid, submission_data):
        if aid in self.assignments:
            self.assignments[aid]["submitted"] = True
            self.assignments[aid]["submission"] = submission_data
            self.assignments[aid]["submitted_at"] = datetime.now().isoformat()
            return True
        return False

    def get_assignment(self, aid):
        return self.assignments.get(aid)

    def list_by_course(self, course_id):
        return [a for a in self.assignments.values()
                if a["course_id"] == course_id]

    def get_pending(self):
        now = datetime.now()
        return [a for a in self.assignments.values()
                if not a["submitted"] and datetime.fromisoformat(a["due_date"]) > now]

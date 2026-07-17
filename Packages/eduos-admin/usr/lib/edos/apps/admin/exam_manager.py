import json
from datetime import datetime

class ExamManager:
    def __init__(self):
        self.exams = {}

    def create_exam(self, eid, name, duration_min, questions=None):
        self.exams[eid] = {
            "id": eid, "name": name, "duration_min": duration_min,
            "questions": questions or [], "status": "draft",
            "created": datetime.now().isoformat()
        }
        return True

    def publish_exam(self, eid):
        if eid in self.exams:
            self.exams[eid]["status"] = "active"
            self.exams[eid]["published"] = datetime.now().isoformat()
            return True
        return False

    def get_results(self, eid):
        exam = self.exams.get(eid)
        if exam:
            return exam.get("results", [])
        return []

    def add_question(self, eid, question_data):
        if eid in self.exams:
            self.exams[eid]["questions"].append(question_data)
            return True
        return False

    def auto_grade(self, eid, submissions):
        exam = self.exams.get(eid)
        if not exam:
            return {}
        grades = {}
        for uid, answers in submissions.items():
            score = 0
            for i, q in enumerate(exam["questions"]):
                if i < len(answers) and q.get("answer") == answers[i]:
                    score += 1
            grades[uid] = {"score": score, "total": len(exam["questions"])}
        return grades

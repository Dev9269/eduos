class ExamEngine:
    def __init__(self):
        self.exams = {}
        self.active_exam = None

    def load_exam(self, exam_data):
        eid = exam_data.get("id", "unknown")
        self.exams[eid] = exam_data
        return eid

    def start_exam(self, eid):
        if eid in self.exams:
            self.active_exam = {"id": eid, "started": True, "answers": {}}
            return True
        return False

    def submit_answer(self, qid, answer):
        if self.active_exam:
            self.active_exam["answers"][qid] = answer
            return True
        return False

    def grade_exam(self):
        if not self.active_exam:
            return {}
        results = {}
        exam = self.exams.get(self.active_exam["id"], {})
        for q in exam.get("questions", []):
            qid = q.get("id")
            correct = q.get("answer")
            given = self.active_exam["answers"].get(qid)
            results[qid] = given == correct
        return results

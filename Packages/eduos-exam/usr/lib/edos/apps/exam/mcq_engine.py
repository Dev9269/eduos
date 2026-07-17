import json

class MCQEngine:
    def __init__(self):
        self.questions = []

    def load_questions(self, filepath):
        try:
            with open(filepath) as f:
                data = json.load(f)
            self.questions = data.get("questions", [])
        except Exception:
            self.questions = []

    def add_question(self, text, options, correct):
        self.questions.append({
            "text": text, "options": options,
            "correct": correct, "type": "mcq"
        })

    def check_answer(self, qid, answer):
        if qid < len(self.questions):
            return self.questions[qid]["correct"] == answer
        return False

    def get_question(self, qid):
        if qid < len(self.questions):
            return self.questions[qid]
        return None

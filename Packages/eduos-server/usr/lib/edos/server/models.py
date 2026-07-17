from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    role: str = "student"
    active: bool = True
    created: str = ""

    def to_dict(self):
        return {"id": self.id, "username": self.username,
                "role": self.role, "active": self.active,
                "created": self.created}

    @classmethod
    def from_row(cls, row):
        return cls(id=row["id"], username=row["username"],
                   role=row["role"], active=bool(row["active"]),
                   created=row["created"])

@dataclass
class Course:
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    code: str = ""
    created: str = ""

    def to_dict(self):
        return {"id": self.id, "name": self.name,
                "description": self.description,
                "code": self.code, "created": self.created}

@dataclass
class Exam:
    id: Optional[int] = None
    name: str = ""
    course_id: int = 0
    duration_min: int = 60
    status: str = "draft"
    created: str = ""
    questions: List[dict] = field(default_factory=list)

    def to_dict(self):
        return {"id": self.id, "name": self.name,
                "course_id": self.course_id,
                "duration_min": self.duration_min,
                "status": self.status, "created": self.created,
                "questions": self.questions}

@dataclass
class Submission:
    id: Optional[int] = None
    exam_id: int = 0
    user_id: int = 0
    answers: dict = field(default_factory=dict)
    score: float = 0.0
    submitted: str = ""

    def to_dict(self):
        return {"id": self.id, "exam_id": self.exam_id,
                "user_id": self.user_id, "answers": self.answers,
                "score": self.score, "submitted": self.submitted}

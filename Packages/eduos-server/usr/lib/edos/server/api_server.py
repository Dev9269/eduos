import json
import os
import sqlite3
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from pydantic import BaseModel
import jwt

try:
    import bcrypt as _bcrypt
    _BCRYPT_OK = True
except ImportError:
    _bcrypt = None
    _BCRYPT_OK = False

from database import Database
from models import User

SECRET_KEY = os.environ.get("EDUOS_JWT_SECRET", "eduos-secret-change-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 480

db: Database = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db
    db = Database()
    db.connect()
    yield
    if db:
        db.close()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        return response


app = FastAPI(title="EduOS Server", version="3.0.0", lifespan=lifespan)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("EDUOS_CORS_ORIGINS", "http://localhost:5050").split(
        ","
    ),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "student"


class CourseCreate(BaseModel):
    name: str
    description: str = ""
    code: str = ""


class ExamCreate(BaseModel):
    name: str
    course_id: int
    duration_min: int = 60
    questions: list = []


class SubmissionCreate(BaseModel):
    exam_id: int
    user_id: int
    answers: dict = {}


def make_token(user_id: int, username: str, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_user_from_header(authorization: str = "") -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid authorization header"
        )
    return decode_token(authorization[7:])


def require_auth(authorization: str = Header(default="")):
    """Dependency — validates Bearer token on protected routes"""
    return get_user_from_header(authorization)


def require_admin(authorization: str = Header(default="")):
    """Dependency — requires admin role"""
    user = get_user_from_header(authorization)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": "3.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/api/auth/login")
async def login(req: LoginRequest):
    if not _BCRYPT_OK:
        raise HTTPException(
            status_code=503,
            detail="Server misconfigured: bcrypt not installed",
        )
    rows = db.query(
        "SELECT * FROM users WHERE username = ? AND active = 1", (req.username,)
    )
    if not rows:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    row = rows[0]
    stored_hash = row["password_hash"] if "password_hash" in row.keys() else ""
    if not stored_hash:
        raise HTTPException(status_code=401, detail="Account not properly configured")
    if not _bcrypt.checkpw(req.password.encode(), stored_hash.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = make_token(row["id"], row["username"], row["role"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": row["id"], "username": row["username"], "role": row["role"]},
    }


@app.post("/api/auth/register")
async def register(req: UserCreate):
    if not _BCRYPT_OK:
        raise HTTPException(
            status_code=503,
            detail="Server misconfigured: bcrypt not installed",
        )
    if not req.password or len(req.password) < 6:
        raise HTTPException(
            status_code=400, detail="Password must be at least 6 characters"
        )
    password_hash = _bcrypt.hashpw(req.password.encode(), _bcrypt.gensalt()).decode()
    try:
        user_id = db.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (req.username, password_hash, req.role),
        )
        token = make_token(user_id, req.username, req.role)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": user_id, "username": req.username, "role": req.role},
        }
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")


@app.get("/api/users")
async def list_users(user=Depends(require_admin)):
    rows = db.query("SELECT * FROM users ORDER BY id")
    return {"users": [User.from_row(r).to_dict() for r in rows], "total": len(rows)}


@app.get("/api/users/{user_id}")
async def get_user(user_id: int, user=Depends(require_admin)):
    rows = db.query("SELECT * FROM users WHERE id = ?", (user_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="User not found")
    return User.from_row(rows[0]).to_dict()


@app.get("/api/courses")
async def list_courses(user=Depends(require_auth)):
    rows = db.query("SELECT * FROM courses ORDER BY id")
    return {"courses": [dict(r) for r in rows], "total": len(rows)}


@app.post("/api/courses")
async def create_course(course: CourseCreate, user=Depends(require_admin)):
    cid = db.execute(
        "INSERT INTO courses (name, description, code) VALUES (?, ?, ?)",
        (course.name, course.description, course.code),
    )
    return {"id": cid, "name": course.name, "status": "created"}


@app.get("/api/exams")
async def list_exams(user=Depends(require_auth)):
    rows = db.query("SELECT * FROM exams ORDER BY id")
    exams = []
    for r in rows:
        e = dict(r)
        e["questions"] = json.loads(e.get("questions") or "[]")
        exams.append(e)
    return {"exams": exams, "total": len(exams)}


@app.post("/api/exams")
async def create_exam(exam: ExamCreate, user=Depends(require_admin)):
    eid = db.execute(
        "INSERT INTO exams (name, course_id, duration_min, questions) VALUES (?, ?, ?, ?)",
        (exam.name, exam.course_id, exam.duration_min, json.dumps(exam.questions)),
    )
    return {"id": eid, "name": exam.name, "status": "created"}


@app.get("/api/exams/{exam_id}")
async def get_exam(exam_id: int, user=Depends(require_auth)):
    rows = db.query("SELECT * FROM exams WHERE id = ?", (exam_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Exam not found")
    e = dict(rows[0])
    e["questions"] = json.loads(e.get("questions") or "[]")
    return e


@app.post("/api/submissions")
async def create_submission(sub: SubmissionCreate, user=Depends(require_auth)):
    sid = db.execute(
        "INSERT INTO submissions (exam_id, user_id, answers) VALUES (?, ?, ?)",
        (sub.exam_id, sub.user_id, json.dumps(sub.answers)),
    )
    return {"id": sid, "status": "submitted"}


@app.get("/api/submissions")
async def list_submissions(user=Depends(require_auth)):
    rows = db.query("SELECT * FROM submissions ORDER BY id")
    subs = []
    for r in rows:
        s = dict(r)
        s["answers"] = json.loads(s.get("answers") or "{}")
        subs.append(s)
    return {"submissions": subs, "total": len(subs)}


@app.post("/api/sync")
async def sync(user=Depends(require_auth)):
    return {"status": "synced", "timestamp": datetime.utcnow().isoformat()}

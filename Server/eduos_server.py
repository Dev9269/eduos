#!/usr/bin/env python3
"""
EduOS Server — runs on the admin's gaming laptop.
Acts as broker between admin panel and all student PC agents.
"""

import asyncio
import json
import logging
import os
import sqlite3
import threading
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict

import websockets
from fastapi import FastAPI, WebSocket, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import jwt
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

SECRET_KEY_FILE = Path('/etc/eduos/server.key')
LOCAL_KEY_FILE = Path.home() / '.eduos' / 'server.key'


def load_or_generate_secret() -> str:
    """Load existing secret key or generate a new one."""
    import secrets

    # Environment variable takes priority
    env_key = os.environ.get('EDUOS_SECRET')
    if env_key and len(env_key) >= 32:
        return env_key

    # Try to load from file
    for key_file in [SECRET_KEY_FILE, LOCAL_KEY_FILE]:
        if key_file.exists():
            try:
                key = key_file.read_text().strip()
                if len(key) >= 32:
                    return key
            except Exception:
                continue

    # Generate new key and save it
    new_key = secrets.token_hex(32)
    save_path = LOCAL_KEY_FILE
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_text(new_key)
    save_path.chmod(0o600)
    log.info(f"Generated new secret key saved to {save_path}")
    return new_key


SECRET_KEY = load_or_generate_secret()
DB_PATH = Path(os.environ.get(
    'EDUOS_DB_PATH',
    str(Path.home() / '.eduos' / 'server.db')  # default to home
))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Connected agents: {hostname: websocket}
connected_agents: Dict[str, WebSocket] = {}

# Active schedule timers: {exam_schedule_id: threading.Timer}
_schedule_timers: Dict[int, threading.Timer] = {}
# Event loop captured when the server starts; timer threads hop onto it
_scheduler_loop: "asyncio.AbstractEventLoop | None" = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler_loop, roster
    try:
        _scheduler_loop = asyncio.get_running_loop()
    except RuntimeError:
        _scheduler_loop = None
    roster = load_roster_from_db()
    init_scheduler()
    yield


app = FastAPI(title="EduOS Server", version="1.0.0", lifespan=lifespan)
security = HTTPBearer()

limiter = Limiter(key_func=get_remote_address, default_limits=[])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY,
        hostname TEXT UNIQUE,
        mac TEXT,
        last_seen TEXT,
        status TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY KEY,
        hostname TEXT,
        command TEXT,
        result TEXT,
        timestamp TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY,
        name TEXT,
        data TEXT,
        created_at TEXT,
        status TEXT DEFAULT "pending"
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY,
        exam_id INTEGER,
        student_id TEXT NOT NULL,
        hostname TEXT,
        answers TEXT NOT NULL,
        submitted_at TEXT NOT NULL,
        checksum TEXT,
        status TEXT DEFAULT "received"
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS updates (
        id INTEGER PRIMARY KEY,
        version TEXT,
        description TEXT,
        files TEXT,
        pushed_at TEXT,
        recipients INTEGER
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS exam_schedules (
        id INTEGER PRIMARY KEY,
        name TEXT,
        data TEXT,
        scheduled_at TEXT,
        status TEXT DEFAULT "scheduled",
        created_at TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS roster (
        student_id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        course TEXT,
        status TEXT DEFAULT "active",
        added_at TEXT
    )''')
    conn.commit()
    conn.close()


def load_roster_from_db() -> dict:
    """Load the roster from the DB into memory."""
    roster = {}
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT student_id, name, email, course, status FROM roster"
        ).fetchall()
        conn.close()
        for r in rows:
            roster[r[0]] = {
                'student_id': r[0], 'name': r[1], 'email': r[2],
                'course': r[3], 'status': r[4],
            }
    except sqlite3.OperationalError:
        pass
    return roster


# In-memory roster: {student_id: {...}}
roster: Dict[str, dict] = {}


def init_scheduler() -> None:
    """Restore pending exam schedules after a server restart."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, data, scheduled_at FROM exam_schedules "
        "WHERE status='scheduled'"
    ).fetchall()
    conn.close()

    for exam_id, data, scheduled_at in rows:
        try:
            when = datetime.fromisoformat(scheduled_at)
            delay = (when - datetime.now()).total_seconds()
        except (ValueError, TypeError):
            delay = -1
        if delay > 0:
            timer = threading.Timer(delay, _scheduled_exam_fired, args=(exam_id,))
            timer.daemon = True
            timer.start()
            _schedule_timers[exam_id] = timer
            log.info(f"Restored schedule: exam={exam_id} in {delay:.0f}s")
        else:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "UPDATE exam_schedules SET status='expired' WHERE id=?",
                (exam_id,)
            )
            conn.commit()
            conn.close()


# Active schedule timers: {exam_schedule_id: threading.Timer}
_schedule_timers: Dict[int, threading.Timer] = {}


def _scheduled_exam_fired(schedule_id: int) -> None:
    """Timer callback — runs in a background thread, so we hop back
    onto the event loop to actually push the exam."""
    loop = _scheduler_loop
    if loop is None or loop.is_closed():
        log.error(f"Schedule {schedule_id} fired but no event loop")
        return
    asyncio.run_coroutine_threadsafe(_start_scheduled_exam(schedule_id), loop)


async def _start_scheduled_exam(schedule_id: int) -> None:
    """Load a schedule, mark it running, and push it to agents."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT name, data FROM exam_schedules WHERE id=?", (schedule_id,)
    ).fetchone()
    conn.close()
    if not row:
        log.warning(f"Schedule {schedule_id} not found at fire time")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE exam_schedules SET status='running' WHERE id=?",
        (schedule_id,)
    )
    conn.commit()
    conn.close()

    name, data_json = row
    try:
        exam_data = json.loads(data_json)
    except json.JSONDecodeError:
        exam_data = {"name": name}

    command = {'action': 'load_exam', 'exam': exam_data}
    recipients = 0
    for host, ws in list(connected_agents.items()):
        try:
            await ws.send_text(json.dumps(command))
            recipients += 1
        except Exception as e:
            log.error(f"Failed to push scheduled exam to {host}: {e}")
    log.info(
        f"Scheduled exam '{name}' (schedule #{schedule_id}) "
        f"started, {recipients} recipients"
    )


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY,
                            algorithms=['HS256'])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/exam/schedules")
async def list_schedules(user=Depends(verify_token)):
    """List all scheduled exams with their status."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """SELECT id, name, scheduled_at, status, created_at
           FROM exam_schedules ORDER BY scheduled_at ASC"""
    ).fetchall()
    conn.close()
    return {"schedules": [
        {"id": r[0], "name": r[1], "scheduled_at": r[2],
         "status": r[3], "created_at": r[4]}
        for r in rows
    ]}


@app.post("/exam/schedule")
async def schedule_exam(schedule: dict, user=Depends(verify_token)):
    """Schedule an exam to be pushed automatically at a future time.
    schedule: {"name": "Midterm 1", "scheduled_at": "2025-06-01T09:00:00",
               "exam": {...exam data...}}
    """
    name = schedule.get('name')
    scheduled_at = schedule.get('scheduled_at')
    exam_data = schedule.get('exam', {})

    if not name or not scheduled_at:
        raise HTTPException(status_code=400,
                            detail="name and scheduled_at are required")
    try:
        when = datetime.fromisoformat(str(scheduled_at).replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400,
                            detail=f"Invalid scheduled_at: {scheduled_at}")
    if when.tzinfo is not None:
        when = when.replace(tzinfo=None)

    delay = (when - datetime.now()).total_seconds()
    if delay <= 0:
        raise HTTPException(status_code=400,
                            detail="scheduled_at must be in the future")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "INSERT INTO exam_schedules (name, data, scheduled_at, created_at) "
        "VALUES (?,?,?,?)",
        (name, json.dumps(exam_data), when.isoformat(),
         datetime.now().isoformat())
    )
    schedule_id = cursor.lastrowid
    conn.commit()
    conn.close()

    timer = threading.Timer(delay, _scheduled_exam_fired, args=(schedule_id,))
    timer.daemon = True
    timer.start()
    _schedule_timers[schedule_id] = timer
    log.info(
        f"Exam '{name}' scheduled for {when.isoformat()} "
        f"(in {delay:.0f}s), schedule id={schedule_id}"
    )
    return {"status": "scheduled", "schedule_id": schedule_id,
            "scheduled_at": when.isoformat()}


@app.delete("/exam/schedule/{schedule_id}")
async def cancel_schedule(schedule_id: int, user=Depends(verify_token)):
    """Cancel a scheduled exam that hasn't started yet."""
    timer = _schedule_timers.pop(schedule_id, None)
    if timer:
        timer.cancel()

    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT status FROM exam_schedules WHERE id=?", (schedule_id,)
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404,
                            detail=f"Schedule {schedule_id} not found")
    if row[0] != 'scheduled':
        conn.close()
        raise HTTPException(status_code=400,
                            detail=f"Cannot cancel schedule in status '{row[0]}'")
    conn.execute(
        "UPDATE exam_schedules SET status='cancelled' WHERE id=?",
        (schedule_id,)
    )
    conn.commit()
    conn.close()
    return {"status": "cancelled", "schedule_id": schedule_id}


@app.get("/roster")
async def get_roster(user=Depends(verify_token)):
    """List all students in the roster."""
    return {
        "total": len(roster),
        "students": list(roster.values()),
    }


@app.post("/roster/add")
async def roster_add(student: dict, user=Depends(verify_token)):
    """Add a student to the roster.
    student: {"student_id": "2021CSE045", "name": "...", "email": "...",
              "course": "..."}
    """
    from Server.roster import validate_student_id

    student_id = (student.get('student_id') or '').strip()
    validation = validate_student_id(student_id)
    if not validation['valid']:
        raise HTTPException(status_code=400,
                            detail=f"Invalid student_id: {validation['reason']}")

    name = (student.get('name') or '').strip()
    email = (student.get('email') or '').strip()
    course = (student.get('course') or '').strip()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """INSERT INTO roster (student_id, name, email, course, added_at)
               VALUES (?,?,?,?,?)""",
            (student_id, name, email, course, datetime.now().isoformat())
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=409,
                            detail=f"{student_id} already in roster")
    conn.close()

    entry = {'student_id': student_id, 'name': name, 'email': email,
             'course': course, 'status': 'active'}
    roster[student_id] = entry
    log.info(f"Roster: added student {student_id}")
    return {"status": "added", "student": entry}


@app.delete("/roster/{student_id}")
async def roster_remove(student_id: str, user=Depends(verify_token)):
    """Remove a student from the roster."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "DELETE FROM roster WHERE student_id=?", (student_id,)
    )
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404,
                            detail=f"{student_id} not in roster")
    roster.pop(student_id, None)
    log.info(f"Roster: removed student {student_id}")
    return {"status": "removed", "student_id": student_id}


@app.post("/roster/validate")
async def roster_validate(payload: dict, user=Depends(verify_token)):
    """Validate a student_id format (and check registry if required).
    payload: {"student_id": "2021CSE045", "check_registered": false}
    """
    from Server.roster import validate_student_id

    student_id = (payload.get('student_id') or '').strip()
    validation = validate_student_id(student_id)
    result = {
        'student_id': student_id,
        'valid_format': validation['valid'],
        'reason': validation['reason'],
        'registered': roster.get(student_id) is not None,
    }
    if payload.get('check_registered'):
        result['valid'] = (validation['valid'] and result['registered'])
        if not result['valid'] and validation['valid']:
            result['reason'] = 'student not in roster'
    else:
        result['valid'] = validation['valid']
    return result


@app.get("/devices")
async def list_devices(user=Depends(verify_token)):
    conn = sqlite3.connect(DB_PATH)
    devices = conn.execute("SELECT * FROM devices").fetchall()
    conn.close()
    return {"devices": devices, "online": list(connected_agents.keys())}


@app.post("/command/{hostname}")
async def send_command(hostname: str, command: dict,
                       user=Depends(verify_token)):
    if hostname == "all":
        results = {}
        for host, ws in connected_agents.items():
            try:
                await ws.send_text(json.dumps(command))
                results[host] = "sent"
            except Exception:
                results[host] = "failed"
        return results

    if hostname not in connected_agents:
        raise HTTPException(status_code=404,
                          detail=f"{hostname} not connected")
    await connected_agents[hostname].send_text(json.dumps(command))
    return {"status": "sent"}


@app.post("/exam/push")
async def push_exam(exam_data: dict, user=Depends(verify_token)):
    """Push exam to all connected agents"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO exams (name, data, created_at) VALUES (?,?,?)",
        (exam_data.get('name'), json.dumps(exam_data),
         datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

    command = {'action': 'load_exam', 'exam': exam_data}
    for host, ws in connected_agents.items():
        try:
            await ws.send_text(json.dumps(command))
        except Exception as e:
            log.error(f"Failed to push exam to {host}: {e}")

    return {"status": "pushed", "recipients": len(connected_agents)}


@app.post("/exam/submit")
@limiter.limit("10/minute")
async def submit_exam(request: Request, submission: dict, user=Depends(verify_token)):
    """Receive exam submission from a student PC agent"""
    import hashlib
    required = ['exam_id', 'student_id', 'answers']
    for field in required:
        if field not in submission:
            raise HTTPException(
                status_code=400,
                detail=f"Missing field: {field}"
            )

    answers_json = json.dumps(submission['answers'])
    checksum = hashlib.sha256(answers_json.encode()).hexdigest()

    student_id = (submission['student_id'] or '').strip()
    if roster and student_id not in roster:
        raise HTTPException(
            status_code=403,
            detail=f"Student {student_id} is not registered in the roster"
        )

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """INSERT INTO submissions
               (exam_id, student_id, hostname, answers,
                submitted_at, checksum)
               VALUES (?,?,?,?,?,?)""",
            (
                submission['exam_id'],
                submission['student_id'],
                submission.get('hostname', 'unknown'),
                answers_json,
                datetime.now().isoformat(),
                checksum
            )
        )
        conn.commit()
        log.info(
            f"Submission received: student={submission['student_id']} "
            f"exam={submission['exam_id']} checksum={checksum[:8]}..."
        )
        return {
            "status": "received",
            "checksum": checksum,
            "submitted_at": datetime.now().isoformat()
        }
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=409, detail=str(e))
    finally:
        conn.close()


@app.get("/exam/submissions/{exam_id}")
async def get_submissions(exam_id: int, user=Depends(verify_token)):
    """Get all submissions for a specific exam"""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """SELECT id, student_id, hostname, submitted_at,
                  checksum, status
           FROM submissions WHERE exam_id=?
           ORDER BY submitted_at ASC""",
        (exam_id,)
    ).fetchall()
    conn.close()
    return {
        "exam_id": exam_id,
        "total": len(rows),
        "submissions": [
            {
                "id": r[0], "student_id": r[1],
                "hostname": r[2], "submitted_at": r[3],
                "checksum": r[4], "status": r[5]
            }
            for r in rows
        ]
    }


@app.get("/exam/submissions/{exam_id}/export")
async def export_submissions(exam_id: int, user=Depends(verify_token)):
    """Export all submissions with full answers for grading"""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT * FROM submissions WHERE exam_id=?",
        (exam_id,)
    ).fetchall()
    conn.close()
    return {
        "exam_id": exam_id,
        "exported_at": datetime.now().isoformat(),
        "submissions": [
            {
                "id": r[0], "exam_id": r[1],
                "student_id": r[2], "hostname": r[3],
                "answers": json.loads(r[4]),
                "submitted_at": r[5],
                "checksum": r[6], "status": r[7]
            }
            for r in rows
        ]
    }


@app.post("/update/push")
async def push_update(update_data: dict, user=Depends(verify_token)):
    """
    Push a software update to all connected student PCs.
    update_data: {
      "version": "1.2.3",
      "description": "Security patch",
      "files": [
        {"path": "relative/path/file.py", "content_b64": "base64..."}
      ],
      "restart_agent": false
    }
    """
    version = update_data.get('version', 'unknown')
    files = update_data.get('files', [])

    if not files:
        raise HTTPException(
            status_code=400,
            detail="No files in update package"
        )

    # Store update in DB
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO updates (version,description,files,pushed_at,recipients) VALUES (?,?,?,?,?)",
        (version, update_data.get('description', ''),
         json.dumps(files), datetime.now().isoformat(),
         len(connected_agents))
    )
    conn.commit()
    conn.close()

    # Broadcast to all agents
    command = {
        'action': 'apply_update',
        'version': version,
        'files': files,
        'restart_agent': update_data.get('restart_agent', False)
    }

    results = {}
    for host, ws in connected_agents.items():
        try:
            await ws.send_text(json.dumps(command))
            results[host] = 'sent'
        except Exception as e:
            results[host] = f'failed: {e}'

    log.info(f"Update v{version} pushed to {len(results)} agents")
    return {
        "status": "pushed",
        "version": version,
        "recipients": results
    }


@app.get("/update/history")
async def update_history(user=Depends(verify_token)):
    """List all pushed updates"""
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT id,version,description,pushed_at,recipients FROM updates ORDER BY id DESC"
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    return {"updates": [
        {"id": r[0], "version": r[1], "description": r[2],
         "pushed_at": r[3], "recipients": r[4]}
        for r in rows
    ]}


@app.post("/update/rollback/{hostname}")
async def rollback_update(hostname: str, rollback_data: dict = None,
                          user=Depends(verify_token)):
    """Ask an agent (or all) to roll back to the previous version.
    rollback_data: {"version": "1.2.3"} to roll back to a specific
    version, or empty for the latest backup."""
    rollback_data = rollback_data or {}
    command = {
        'action': 'rollback',
        'version': rollback_data.get('version'),
    }

    if hostname == "all":
        results = {}
        for host, ws in connected_agents.items():
            try:
                await ws.send_text(json.dumps(command))
                results[host] = "rollback_sent"
            except Exception:
                results[host] = "failed"
        log.info(f"Rollback requested for all {len(results)} agents")
        return {"status": "rollback_requested", "recipients": results}

    if hostname not in connected_agents:
        raise HTTPException(status_code=404,
                            detail=f"{hostname} not connected")
    await connected_agents[hostname].send_text(json.dumps(command))
    log.info(f"Rollback requested for {hostname}")
    return {"status": "rollback_requested", "hostname": hostname}


@app.get("/exam/submissions/{exam_id}/similarity")
async def check_similarity(exam_id: int, user=Depends(verify_token)):
    """Check all submissions for code similarity"""
    from Server.similarity import check_submissions_for_similarity

    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT student_id, answers FROM submissions WHERE exam_id=?",
        (exam_id,)
    ).fetchall()
    conn.close()

    subs = [
        {'student_id': r[0], 'answers': json.loads(r[1])}
        for r in rows
    ]
    suspicious = check_submissions_for_similarity(subs)
    return {
        "exam_id": exam_id,
        "total_checked": len(subs),
        "suspicious_pairs": len(suspicious),
        "results": suspicious
    }


@app.get("/health")
@limiter.limit("60/minute")
async def health(request: Request):
    """Simple health check for monitoring probes."""
    return {"status": "ok", "time": datetime.now().isoformat()}


@app.websocket("/ws/agent")
async def agent_websocket(websocket: WebSocket):
    await websocket.accept()
    hostname = None
    try:
        # Wait for registration
        data = json.loads(await websocket.receive_text())
        if data.get('type') == 'register':
            hostname = data['hostname']
            connected_agents[hostname] = websocket
            log.info(f"Agent registered: {hostname}")

            # Update DB
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "INSERT OR REPLACE INTO devices (hostname, mac, last_seen, status) VALUES (?,?,?,?)",
                (hostname, data.get('mac', ''),
                 datetime.now().isoformat(), 'online')
            )
            conn.commit()
            conn.close()

        # Keep connection alive
        async for message in websocket.iter_text():
            log.info(f"[{hostname}] {message}")

    except Exception as e:
        log.error(f"Agent connection error: {e}")
    finally:
        if hostname and hostname in connected_agents:
            del connected_agents[hostname]
            log.info(f"Agent disconnected: {hostname}")


if __name__ == '__main__':
    init_db()
    uvicorn.run(app, host='0.0.0.0', port=8765, log_level='info')

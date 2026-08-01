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
from datetime import datetime
from pathlib import Path
from typing import Dict

import websockets
from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import jwt

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

app = FastAPI(title="EduOS Server", version="1.0.0")
security = HTTPBearer()

# Connected agents: {hostname: websocket}
connected_agents: Dict[str, WebSocket] = {}


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
    conn.commit()
    conn.close()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY,
                            algorithms=['HS256'])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


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
async def submit_exam(submission: dict, user=Depends(verify_token)):
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

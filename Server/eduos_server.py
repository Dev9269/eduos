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

SECRET_KEY = os.environ.get('EDUOS_SECRET', 'change-this-in-production')
DB_PATH = Path(os.environ.get('EDUOS_DB_PATH', '/var/lib/eduos/server.db'))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

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

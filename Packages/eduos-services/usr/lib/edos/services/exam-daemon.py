#!/usr/bin/env python3
"""
EduOS Exam Daemon — polls local EduOS server for active exams.
Runs as a FreeBSD rc.d service or Linux systemd unit.
Activates/deactivates exam lockdown based on server commands.
"""
import syslog
import time
import json
import urllib.request
import subprocess
import platform
import os
from pathlib import Path

CONFIG_FILE = Path("/etc/eduos/agent.conf")
LOCAL_CONFIG = Path.home() / ".eduos" / "agent.conf"
POLL_INTERVAL = 15  # seconds


def load_config() -> dict:
    for p in [CONFIG_FILE, LOCAL_CONFIG]:
        if p.exists():
            try:
                return json.loads(p.read_text())
            except Exception:
                continue
    return {"server_url": "ws://eduos-server.local:8765", "token": ""}


def get_server_http(config: dict) -> str:
    return config["server_url"].replace("ws://", "http://").replace("wss://", "https://")


def fetch_schedules(server_http: str, token: str) -> list:
    try:
        req = urllib.request.Request(
            f"{server_http}/exam/schedules",
            headers={"Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("schedules", [])
    except Exception as e:
        syslog.syslog(syslog.LOG_WARNING, f"EduOS Exam Daemon: server unreachable: {e}")
        return []


def activate_exam(exam_name: str):
    syslog.syslog(syslog.LOG_INFO, f"EduOS Exam Daemon: activating exam: {exam_name}")
    if platform.system() == "FreeBSD":
        subprocess.run(["service", "eduos_exam", "start"], check=False)
    else:
        subprocess.run(["systemctl", "start", "eduos-exam-lock"], check=False)


def deactivate_exam():
    syslog.syslog(syslog.LOG_INFO, "EduOS Exam Daemon: deactivating exam mode")
    if platform.system() == "FreeBSD":
        subprocess.run(["service", "eduos_exam", "stop"], check=False)
    else:
        subprocess.run(["systemctl", "stop", "eduos-exam-lock"], check=False)


def main():
    syslog.openlog("eduos-exam-daemon", syslog.LOG_PID, syslog.LOG_DAEMON)
    syslog.syslog(syslog.LOG_INFO, "EduOS Exam Daemon started")

    exam_was_active = False
    fail_count = 0

    while True:
        try:
            config = load_config()
            server_http = get_server_http(config)
            token = config.get("token", "")

            schedules = fetch_schedules(server_http, token)
            currently_active = [
                s for s in schedules if s.get("status") == "activated"
            ]

            if currently_active and not exam_was_active:
                activate_exam(currently_active[0].get("exam_name", "Unknown"))
                exam_was_active = True
            elif not currently_active and exam_was_active:
                deactivate_exam()
                exam_was_active = False

            fail_count = 0

        except Exception as e:
            syslog.syslog(syslog.LOG_ERR, f"EduOS Exam Daemon error: {e}")
            fail_count += 1

        # Bounded exponential backoff: double the wait on each failure,
        # capped at 300s so a long outage never hammers the network.
        time.sleep(min(300, POLL_INTERVAL * (2 ** min(fail_count, 5))))


if __name__ == "__main__":
    main()

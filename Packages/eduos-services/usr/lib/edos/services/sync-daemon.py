#!/usr/bin/env python3
"""EduOS Sync Daemon — syncs data between student machines and server"""
import syslog
import time
import json
import urllib.request
import platform
from pathlib import Path

CONFIG_FILE = Path("/etc/eduos/agent.conf")
LOCAL_CONFIG = Path.home() / ".eduos" / "agent.conf"
POLL_INTERVAL = 30


def load_config():
    for p in [CONFIG_FILE, LOCAL_CONFIG]:
        if p.exists():
            try:
                return json.loads(p.read_text())
            except Exception:
                continue
    return {"server_url": "ws://eduos-server.local:8765", "token": ""}


def sync_once(server_http, token):
    req = urllib.request.Request(
        f"{server_http}/api/sync",
        data=b"{}",
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def main():
    syslog.openlog("eduos-sync", syslog.LOG_PID, syslog.LOG_DAEMON)
    syslog.syslog(syslog.LOG_INFO, "EduOS Sync Daemon started")
    fail_count = 0
    while True:
        try:
            config = load_config()
            server_http = config["server_url"].replace("ws://", "http://")
            token = config.get("token", "")
            result = sync_once(server_http, token)
            syslog.syslog(syslog.LOG_DEBUG, f"Sync OK: {result}")
            fail_count = 0
        except Exception as e:
            fail_count += 1
            wait = min(300, POLL_INTERVAL * (2 ** min(fail_count, 5)))
            syslog.syslog(syslog.LOG_WARNING, f"Sync failed ({fail_count}): {e}")
            time.sleep(wait)
            continue
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()

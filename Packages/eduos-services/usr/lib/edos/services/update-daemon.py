#!/usr/bin/env python3
"""EduOS Update Daemon — polls local EduOS server for available updates"""
import syslog
import time
import json
import urllib.request
import platform
from pathlib import Path

CONFIG_FILE = Path("/etc/eduos/agent.conf")
LOCAL_CONFIG = Path.home() / ".eduos" / "agent.conf"
LOCAL_VERSION = "3.0.0"
POLL_INTERVAL = 3600


def load_config():
    for p in [CONFIG_FILE, LOCAL_CONFIG]:
        if p.exists():
            try:
                return json.loads(p.read_text())
            except Exception:
                continue
    return {"server_url": "ws://eduos-server.local:8765", "token": ""}


def check_for_updates(server_http, token):
    req = urllib.request.Request(
        f"{server_http}/api/updates/check?version={LOCAL_VERSION}",
        headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def main():
    syslog.openlog("edos-update", syslog.LOG_PID, syslog.LOG_DAEMON)
    syslog.syslog(syslog.LOG_INFO, "EduOS Update Daemon started")
    fail_count = 0
    while True:
        try:
            config = load_config()
            server_http = config["server_url"].replace("ws://", "http://")
            token = config.get("token", "")
            data = check_for_updates(server_http, token)
            if data.get("update_available"):
                syslog.syslog(
                    syslog.LOG_WARNING,
                    f"Update available: {data.get('version')}",
                )
            else:
                syslog.syslog(syslog.LOG_DEBUG, "No updates available")
            fail_count = 0
        except Exception as e:
            fail_count += 1
            wait = min(7200, POLL_INTERVAL * (2 ** min(fail_count, 5)))
            syslog.syslog(syslog.LOG_WARNING, f"Update check failed ({fail_count}): {e}")
            time.sleep(wait)
            continue
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()

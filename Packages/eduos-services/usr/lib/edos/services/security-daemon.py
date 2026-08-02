#!/usr/bin/env python3
"""EduOS Security Daemon — enforces local security policies on student machines"""
import syslog
import time
import json
import subprocess
import shlex
import platform
from pathlib import Path

CONFIG_FILE = Path("/etc/eduos/agent.conf")
LOCAL_CONFIG = Path.home() / ".eduos" / "agent.conf"
POLICY_FILE = Path("/etc/eduos/security-policy.json")
CHECK_INTERVAL = 120


def load_config():
    for p in [CONFIG_FILE, LOCAL_CONFIG]:
        if p.exists():
            try:
                return json.loads(p.read_text())
            except Exception:
                continue
    return {"server_url": "ws://eduos-server.local:8765", "token": ""}


def check_policies():
    try:
        with open(POLICY_FILE) as f:
            policies = json.load(f)
        for policy in policies.get("rules", []):
            cmd = policy.get("check", "")
            if not cmd:
                continue
            cmd_args = shlex.split(cmd)
            result = subprocess.run(
                cmd_args, capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                syslog.syslog(
                    syslog.LOG_WARNING,
                    f"Policy violation: {policy.get('name')} - {result.stderr.strip()}",
                )
    except FileNotFoundError:
        syslog.syslog(syslog.LOG_DEBUG, "No policy file found")
    except subprocess.TimeoutExpired:
        syslog.syslog(syslog.LOG_WARNING, "Security check timed out")
    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, f"Security check error: {e}")


def main():
    syslog.openlog("edos-security", syslog.LOG_PID, syslog.LOG_DAEMON)
    syslog.syslog(syslog.LOG_INFO, "EduOS Security Daemon started")

    config = load_config()
    syslog.syslog(
        syslog.LOG_DEBUG,
        f"EduOS Security Daemon: configured for {config.get('server_url', 'unknown')}",
    )

    fail_count = 0
    while True:
        try:
            check_policies()
            fail_count = 0
        except Exception as e:
            fail_count += 1
            wait = min(600, CHECK_INTERVAL * (2 ** min(fail_count, 5)))
            syslog.syslog(syslog.LOG_WARNING, f"Security check failed ({fail_count}): {e}")
            time.sleep(wait)
            continue
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()

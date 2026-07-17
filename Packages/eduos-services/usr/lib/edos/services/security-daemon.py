#!/usr/bin/env python3
import syslog
import time
import json
import subprocess

POLICY_FILE = "/etc/edos/security-policy.json"
CHECK_INTERVAL = 120

import shlex


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
    while True:
        check_policies()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()

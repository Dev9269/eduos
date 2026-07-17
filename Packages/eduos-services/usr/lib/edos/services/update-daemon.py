#!/usr/bin/env python3
import syslog
import time
import json
import urllib.request

UPDATE_URL = "https://update.edos.edu/api/check"
LOCAL_VERSION = "3.0.0"

def main():
    syslog.openlog("edos-update", syslog.LOG_PID, syslog.LOG_DAEMON)
    syslog.syslog(syslog.LOG_INFO, "EduOS Update Daemon started")
    while True:
        try:
            req = urllib.request.Request(f"{UPDATE_URL}?version={LOCAL_VERSION}")
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                if data.get("update_available"):
                    syslog.syslog(syslog.LOG_WARNING, f"Update available: {data.get('version')}")
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR, f"Update check error: {e}")
        time.sleep(3600)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import syslog
import time
import json
import urllib.request

SERVER_URL = "https://sync.edos.edu/api/poll"

def main():
    syslog.openlog("edos-sync", syslog.LOG_PID, syslog.LOG_DAEMON)
    syslog.syslog(syslog.LOG_INFO, "EduOS Sync Daemon started")
    while True:
        try:
            req = urllib.request.Request(SERVER_URL)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                syslog.syslog(syslog.LOG_INFO, f"Sync response: {data.get('status', 'unknown')}")
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR, f"Sync error: {e}")
        time.sleep(60)

if __name__ == "__main__":
    main()

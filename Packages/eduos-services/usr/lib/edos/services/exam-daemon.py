#!/usr/bin/env python3
import syslog
import time
import json
import urllib.request

EXAM_STATUS_URL = "https://exam.edos.edu/api/status"

def main():
    syslog.openlog("edos-exam", syslog.LOG_PID, syslog.LOG_DAEMON)
    syslog.syslog(syslog.LOG_INFO, "EduOS Exam Daemon started")
    while True:
        try:
            req = urllib.request.Request(EXAM_STATUS_URL)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                if data.get("exam_active"):
                    syslog.syslog(syslog.LOG_INFO, f"Active exam: {data.get('exam_name')}")
                else:
                    syslog.syslog(syslog.LOG_DEBUG, "No active exam")
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR, f"Exam status error: {e}")
        time.sleep(30)

if __name__ == "__main__":
    main()

import json
import urllib.request
import subprocess
from datetime import datetime

class UpdateEngine:
    def __init__(self):
        self.current_version = "3.0.0"
        self.update_server = "https://update.edos.edu/api"

    def check_for_updates(self):
        try:
            url = f"{self.update_server}/check?version={self.current_version}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                return data.get("updates", [])
        except Exception as e:
            return {"error": str(e), "updates": []}

    def download_update(self, package_name, version):
        try:
            url = f"{self.update_server}/download/{package_name}/{version}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = resp.read()
                return {"status": "downloaded", "size": len(data)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def install_update(self, package_name):
        try:
            result = subprocess.run(
                ["apt-get", "install", "-y", package_name],
                capture_output=True, text=True, timeout=300
            )
            return {"status": "ok" if result.returncode == 0 else "error",
                    "output": result.stdout + result.stderr}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_update_history(self):
        return [
            {"date": "2026-01-01", "version": "3.0.0",
             "packages": ["all"], "status": "installed"}
        ]

    def check_disk_space(self):
        try:
            result = subprocess.run(["df", "-h", "/"],
                capture_output=True, text=True, timeout=5)
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                return {"total": parts[1], "used": parts[2],
                        "available": parts[3], "percent": parts[4]}
        except Exception:
            pass
        return {"available": "unknown"}

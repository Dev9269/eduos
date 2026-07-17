import json
import urllib.request

class UpdateManager:
    def __init__(self):
        self.current_version = "3.0.0"
        self.update_url = "https://update.edos.edu/api/check"

    def check_for_updates(self):
        try:
            req = urllib.request.Request(
                f"{self.update_url}?version={self.current_version}")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                return data
        except Exception:
            return {"update_available": False, "error": "Cannot reach update server"}

    def deploy_update(self, version):
        return {"status": "deployed", "version": version}

    def get_version_history(self):
        return [
            {"version": "3.0.0", "date": "2026-01-01", "changes": "Initial v3 release"}
        ]

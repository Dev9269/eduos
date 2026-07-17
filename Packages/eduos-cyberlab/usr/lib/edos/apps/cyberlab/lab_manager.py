import json
from datetime import datetime

class LabManager:
    def __init__(self):
        self.labs = {}

    def create_lab(self, lid, name, description, objectives, tools_needed, duration_min):
        self.labs[lid] = {
            "id": lid, "name": name, "description": description,
            "objectives": objectives, "tools_needed": tools_needed,
            "duration_min": duration_min, "status": "available",
            "created": datetime.now().isoformat()
        }
        return True

    def start_lab(self, lid):
        if lid in self.labs:
            self.labs[lid]["status"] = "in_progress"
            self.labs[lid]["started"] = datetime.now().isoformat()
            return True
        return False

    def complete_lab(self, lid, results):
        if lid in self.labs:
            self.labs[lid]["status"] = "completed"
            self.labs[lid]["results"] = results
            self.labs[lid]["completed"] = datetime.now().isoformat()
            return True
        return False

    def get_lab(self, lid):
        return self.labs.get(lid)

    def list_available(self):
        return [l for l in self.labs.values() if l["status"] == "available"]

    def save(self, filepath):
        with open(filepath, "w") as f:
            json.dump(self.labs, f, indent=2)

from datetime import datetime


class DeviceManager:
    def __init__(self):
        self.devices = {}

    def register_device(self, did, name, dtype="Workstation"):
        self.devices[did] = {
            "id": did,
            "name": name,
            "type": dtype,
            "status": "offline",
            "last_sync": None,
            "locked": False,
            "registered": datetime.now().isoformat(),
        }
        return True

    def update_status(self, did, status):
        if did in self.devices:
            self.devices[did]["status"] = status
            self.devices[did]["last_sync"] = datetime.now().isoformat()
            return True
        return False

    def get_device(self, did):
        return self.devices.get(did)

    def list_by_status(self, status):
        return [d for d in self.devices.values() if d["status"] == status]

    def lock_device(self, did):
        if did in self.devices:
            self.devices[did]["locked"] = True
            self.devices[did]["status"] = "locked"
            return True
        return False

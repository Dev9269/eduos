import json

class UserManager:
    def __init__(self):
        self.users = {}

    def create_user(self, uid, username, role="Student", password_hash=""):
        self.users[uid] = {
            "id": uid, "username": username, "role": role,
            "password_hash": password_hash, "active": True,
            "created": "2026-01-01T00:00:00"
        }
        return True

    def deactivate_user(self, uid):
        if uid in self.users:
            self.users[uid]["active"] = False
            return True
        return False

    def get_user(self, uid):
        return self.users.get(uid)

    def list_by_role(self, role):
        return [u for u in self.users.values() if u["role"] == role]

    def save(self, filepath):
        with open(filepath, "w") as f:
            json.dump(self.users, f, indent=2)

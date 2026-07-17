import json

class Panels:
    def __init__(self):
        self.settings = {}

    def get_panel(self, name):
        panels = {
            "appearance": self._appearance_panel,
            "system": self._system_panel,
            "network": self._network_panel,
            "privacy": self._privacy_panel,
        }
        return panels.get(name, self._empty_panel)()

    def _appearance_panel(self):
        return {
            "name": "Appearance",
            "fields": [
                {"key": "theme", "type": "choice", "options": ["dark", "light", "system"]},
                {"key": "accent", "type": "choice", "options": ["cyan", "blue", "green"]},
                {"key": "font_size", "type": "int", "default": 10},
            ]
        }

    def _system_panel(self):
        return {
            "name": "System",
            "fields": [
                {"key": "timezone", "type": "string", "default": "UTC"},
                {"key": "auto_update", "type": "bool", "default": True},
            ]
        }

    def _network_panel(self):
        return {
            "name": "Network",
            "fields": [
                {"key": "proxy_enabled", "type": "bool", "default": False},
                {"key": "proxy_host", "type": "string", "default": ""},
                {"key": "proxy_port", "type": "int", "default": 8080},
            ]
        }

    def _privacy_panel(self):
        return {
            "name": "Privacy",
            "fields": [
                {"key": "telemetry", "type": "bool", "default": False},
                {"key": "location", "type": "bool", "default": False},
            ]
        }

    def _empty_panel(self):
        return {"name": "Unknown", "fields": []}

    def validate(self, panel_name, values):
        panel = self.get_panel(panel_name)
        errors = []
        for field in panel["fields"]:
            key = field["key"]
            if key not in values:
                errors.append(f"Missing field: {key}")
        return errors

    def save_settings(self, filepath, settings):
        with open(filepath, "w") as f:
            json.dump(settings, f, indent=2)

    def load_settings(self, filepath):
        try:
            with open(filepath) as f:
                return json.load(f)
        except Exception:
            return {}

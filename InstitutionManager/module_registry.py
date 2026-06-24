"""
EduOS Institution Manager — Module Registry
Central system for enabling, disabling, installing, removing, and configuring modules.
"""

import json
from datetime import datetime
from config import load_json, save_json, PATHS, log_activity

MODULE_CATALOG = {
    "learn_hub": {
        "id": "learn_hub", "name": "Learn Hub", "description": "Student learning portal with courses, assignments, and study materials",
        "version": "2.1.0", "size_mb": 48, "dependencies": [], "category": "Learning"
    },
    "exam_hub": {
        "id": "exam_hub", "name": "Exam Hub", "description": "Secure examination platform with auto-grading and analytics",
        "version": "2.0.0", "size_mb": 32, "dependencies": ["learn_hub"], "category": "Assessment"
    },
    "dev_suite": {
        "id": "dev_suite", "name": "Dev Suite", "description": "Integrated development environment with multiple language support",
        "version": "1.9.0", "size_mb": 156, "dependencies": [], "category": "Development"
    },
    "cyber_lab": {
        "id": "cyber_lab", "name": "Cyber Lab", "description": "Isolated container-based cybersecurity practice environment",
        "version": "1.8.0", "size_mb": 210, "dependencies": ["dev_suite"], "category": "Security"
    },
    "library": {
        "id": "library", "name": "Library Management", "description": "Digital library with catalog, borrowing, and resource management",
        "version": "1.0.0", "size_mb": 24, "dependencies": [], "category": "Administration"
    },
    "attendance": {
        "id": "attendance", "name": "Attendance Management", "description": "Automated attendance tracking with biometric integration",
        "version": "1.0.0", "size_mb": 18, "dependencies": [], "category": "Administration"
    },
    "placement": {
        "id": "placement", "name": "Placement Cell", "description": "Campus recruitment management and career development platform",
        "version": "1.0.0", "size_mb": 28, "dependencies": ["learn_hub"], "category": "Career"
    },
    "research": {
        "id": "research", "name": "Research Portal", "description": "Research paper management, citation tools, and collaboration",
        "version": "1.0.0", "size_mb": 36, "dependencies": ["library"], "category": "Research"
    },
    "ai_assistant": {
        "id": "ai_assistant", "name": "AI Assistant", "description": "AI-powered learning assistant for concept explanation and practice",
        "version": "1.0.0", "size_mb": 12, "dependencies": [], "category": "AI"
    },
}


class ModuleRegistry:
    def __init__(self):
        self.registry = self._load()

    def _load(self):
        default = {mid: {
            "id": mid, "name": cat["name"], "version": cat["version"],
            "enabled": mid in ("learn_hub", "exam_hub", "dev_suite", "cyber_lab", "ai_assistant"),
            "installed": mid in ("learn_hub", "exam_hub", "dev_suite", "cyber_lab", "ai_assistant"),
            "install_date": datetime.now().isoformat() if mid in ("learn_hub", "exam_hub", "dev_suite", "cyber_lab", "ai_assistant") else "",
            "config": {}
        } for mid, cat in MODULE_CATALOG.items()}
        saved = load_json(PATHS["modules"], default)
        for mid in MODULE_CATALOG:
            if mid not in saved:
                saved[mid] = default[mid]
        return saved

    def save(self):
        save_json(PATHS["modules"], self.registry)

    def list_modules(self):
        return [self._enrich(mid) for mid in MODULE_CATALOG]

    def _enrich(self, mid):
        state = self.registry.get(mid, {})
        cat = MODULE_CATALOG.get(mid, {})
        return {**cat, **state}

    def get_module(self, mid):
        return self._enrich(mid)

    def enable(self, mid):
        if mid in self.registry and self.registry[mid].get("installed"):
            self.registry[mid]["enabled"] = True
            self.save()
            log_activity("Module Enabled", f"{MODULE_CATALOG[mid]['name']} enabled")
            return True, f"{MODULE_CATALOG[mid]['name']} enabled"
        return False, "Module not installed"

    def disable(self, mid):
        if mid in self.registry:
            self.registry[mid]["enabled"] = False
            self.save()
            log_activity("Module Disabled", f"{MODULE_CATALOG[mid]['name']} disabled")
            return True, f"{MODULE_CATALOG[mid]['name']} disabled"
        return False, "Module not found"

    def install(self, mid):
        if mid in MODULE_CATALOG:
            deps = MODULE_CATALOG[mid].get("dependencies", [])
            for d in deps:
                if d not in self.registry or not self.registry[d].get("installed"):
                    return False, f"Dependency required: {MODULE_CATALOG[d]['name']}"
            self.registry[mid] = {
                "id": mid, "name": MODULE_CATALOG[mid]["name"],
                "version": MODULE_CATALOG[mid]["version"],
                "enabled": True, "installed": True,
                "install_date": datetime.now().isoformat(), "config": {}
            }
            self.save()
            log_activity("Module Installed", f"{MODULE_CATALOG[mid]['name']} installed")
            return True, f"{MODULE_CATALOG[mid]['name']} installed"
        return False, "Module not found in catalog"

    def remove(self, mid):
        if mid in self.registry and self.registry[mid].get("installed"):
            dependents = [m for m, s in self.registry.items()
                          if s.get("installed") and mid in MODULE_CATALOG.get(m, {}).get("dependencies", [])]
            if dependents:
                names = [MODULE_CATALOG[d]["name"] for d in dependents]
                return False, f"Cannot remove: required by {', '.join(names)}"
            self.registry[mid] = {
                "id": mid, "name": MODULE_CATALOG[mid]["name"],
                "version": MODULE_CATALOG[mid]["version"],
                "enabled": False, "installed": False,
                "install_date": "", "config": {}
            }
            self.save()
            log_activity("Module Removed", f"{MODULE_CATALOG[mid]['name']} removed")
            return True, f"{MODULE_CATALOG[mid]['name']} removed"
        return False, "Module not found"

    def configure(self, mid, config_data):
        if mid in self.registry:
            self.registry[mid]["config"] = config_data
            self.save()
            log_activity("Module Configured", f"{MODULE_CATALOG[mid]['name']} configured")
            return True, f"{MODULE_CATALOG[mid]['name']} configured"
        return False, "Module not found"

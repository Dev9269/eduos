"""
EduOS Institution Manager — Configuration & Storage Layer
"""

import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path.home() / ".eduos" / "institution"
BASE_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
EXPORTS_DIR = BASE_DIR / "exports"
EXPORTS_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

PATHS = {
    "institution": BASE_DIR / "institution.json",
    "modules": BASE_DIR / "modules.json",
    "branding": BASE_DIR / "branding.json",
    "departments": DATA_DIR / "departments.json",
    "courses": DATA_DIR / "courses.json",
    "students": DATA_DIR / "students.json",
    "faculty": DATA_DIR / "faculty.json",
    "labs": DATA_DIR / "labs.json",
    "exams": DATA_DIR / "exams.json",
    "devices": DATA_DIR / "devices.json",
    "updates": DATA_DIR / "updates.json",
    "activity": DATA_DIR / "activity.json",
    "analytics": DATA_DIR / "analytics.json",
    "ai_config": DATA_DIR / "ai_config.json",
}


def load_json(path, default=None):
    try:
        if path.exists():
            with open(path) as f:
                return json.load(f)
    except Exception:
        pass
    return default if default is not None else {}


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def institution_config():
    return load_json(PATHS["institution"], {
        "name": "My Institution",
        "type": "University",
        "address": "",
        "city": "",
        "country": "",
        "phone": "",
        "email": "",
        "website": "",
        "established": "2024",
        "accreditation": "",
        "principal": "",
        "student_count": 0,
        "faculty_count": 0,
        "departments": 0,
        "version": "1.0.0"
    })


def save_institution(cfg):
    save_json(PATHS["institution"], cfg)


def module_registry():
    return load_json(PATHS["modules"], {
        "learn_hub": {"id": "learn_hub", "name": "Learn Hub", "version": "2.1.0", "enabled": True, "installed": True, "config": {}},
        "exam_hub": {"id": "exam_hub", "name": "Exam Hub", "version": "2.0.0", "enabled": True, "installed": True, "config": {}},
        "dev_suite": {"id": "dev_suite", "name": "Dev Suite", "version": "1.9.0", "enabled": True, "installed": True, "config": {}},
        "cyber_lab": {"id": "cyber_lab", "name": "Cyber Lab", "version": "1.8.0", "enabled": True, "installed": True, "config": {}},
        "library": {"id": "library", "name": "Library Management", "version": "1.0.0", "enabled": False, "installed": False, "config": {}},
        "attendance": {"id": "attendance", "name": "Attendance Management", "version": "1.0.0", "enabled": False, "installed": False, "config": {}},
        "placement": {"id": "placement", "name": "Placement Cell", "version": "1.0.0", "enabled": False, "installed": False, "config": {}},
        "research": {"id": "research", "name": "Research Portal", "version": "1.0.0", "enabled": False, "installed": False, "config": {}},
        "ai_assistant": {"id": "ai_assistant", "name": "AI Assistant", "version": "1.0.0", "enabled": True, "installed": True, "config": {}}
    })


def save_registry(reg):
    save_json(PATHS["modules"], reg)


def branding_config():
    return load_json(PATHS["branding"], {
        "institution_name": "My Institution",
        "short_name": "MI",
        "logo_path": "",
        "wallpaper_path": "",
        "primary_color": "#2563eb",
        "secondary_color": "#1e40af",
        "login_message": "Welcome to EduOS",
        "welcome_title": "Welcome to EduOS",
        "welcome_subtitle": "Your Educational Operating System",
        "custom_css": ""
    })


def save_branding(cfg):
    save_json(PATHS["branding"], cfg)


def get_activity_log(limit=50):
    acts = load_json(PATHS["activity"], [])
    return acts[:limit]


def log_activity(action, details=""):
    acts = load_json(PATHS["activity"], [])
    acts.insert(0, {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details
    })
    save_json(PATHS["activity"], acts[:200])


def get_analytics():
    return load_json(PATHS["analytics"], {
        "total_students": 0, "total_faculty": 0,
        "active_courses": 0, "total_exams": 0,
        "pass_rate": 0, "avg_score": 0,
        "device_count": 0, "online_devices": 0,
        "active_labs": 0, "storage_used_gb": 0
    })

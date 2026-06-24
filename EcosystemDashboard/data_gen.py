"""
EduOS Ecosystem Dashboard — Realistic Demo Data Generator
"""

import json
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

random.seed(42)

INSTITUTION = {
    "name": "Parul University",
    "type": "University",
    "short": "PU",
    "address": "Post Limda, Waghodia, Vadodara, Gujarat",
    "established": "2015",
    "accreditation": "NAAC A+",
    "principal": "Dr. Parul Shah",
    "students": 8472,
    "faculty": 684,
    "staff": 312,
    "departments": 12,
    "programs": 48,
    "campuses": 3,
    "labs": 42,
    "classrooms": 186,
    "total_devices": 5280,
    "online_devices": 4892,
}

DEPARTMENTS = [
    {"id": "CSE", "name": "Computer Science & Engineering", "students": 1850, "faculty": 86, "hod": "Dr. Arvind Kumar"},
    {"id": "ECE", "name": "Electronics & Communication", "students": 1120, "faculty": 58, "hod": "Dr. Sunita Patel"},
    {"id": "ME", "name": "Mechanical Engineering", "students": 890, "faculty": 48, "hod": "Dr. Rajesh Singh"},
    {"id": "CE", "name": "Civil Engineering", "students": 720, "faculty": 38, "hod": "Dr. Priya Sharma"},
    {"id": "EE", "name": "Electrical Engineering", "students": 650, "faculty": 35, "hod": "Dr. Amit Verma"},
    {"id": "IT", "name": "Information Technology", "students": 1340, "faculty": 62, "hod": "Dr. Neha Gupta"},
    {"id": "MBA", "name": "Business Administration", "students": 580, "faculty": 28, "hod": "Dr. Rohit Mehta"},
    {"id": "BS", "name": "Basic Sciences", "students": 1322, "faculty": 72, "hod": "Dr. Deepa Iyer"},
    {"id": "PH", "name": "Pharmacy", "students": 450, "faculty": 24, "hod": "Dr. Kavita Desai"},
    {"id": "BT", "name": "Biotechnology", "students": 280, "faculty": 18, "hod": "Dr. Aniket Joshi"},
    {"id": "ARCH", "name": "Architecture", "students": 190, "faculty": 14, "hod": "Dr. Meera Nair"},
    {"id": "LAW", "name": "Law", "students": 480, "faculty": 32, "hod": "Dr. Prakash Iyer"},
]

MODULES = [
    {"id": "learn_hub", "name": "Learn Hub", "icon": "📚", "version": "2.1.0", "size_mb": 48, "status": "installed", "enabled": True, "category": "Learning", "ram_mb": 128, "cpu_pct": 4.2},
    {"id": "exam_hub", "name": "Exam Hub", "icon": "📝", "version": "2.0.0", "size_mb": 32, "status": "installed", "enabled": True, "category": "Assessment", "ram_mb": 96, "cpu_pct": 3.8},
    {"id": "dev_suite", "name": "Dev Suite", "icon": "💻", "version": "1.9.0", "size_mb": 156, "status": "installed", "enabled": True, "category": "Development", "ram_mb": 256, "cpu_pct": 8.5},
    {"id": "cyber_lab", "name": "Cyber Lab", "icon": "🛡️", "version": "1.8.0", "size_mb": 210, "status": "installed", "enabled": True, "category": "Security", "ram_mb": 512, "cpu_pct": 12.0},
    {"id": "ai_assistant", "name": "AI Assistant", "icon": "🤖", "version": "1.0.0", "size_mb": 12, "status": "installed", "enabled": True, "category": "AI", "ram_mb": 64, "cpu_pct": 2.1},
    {"id": "library", "name": "Library Management", "icon": "📖", "version": "1.0.0", "size_mb": 24, "status": "not_installed", "enabled": False, "category": "Administration", "ram_mb": 48, "cpu_pct": 1.5},
    {"id": "attendance", "name": "Attendance System", "icon": "✅", "version": "1.0.0", "size_mb": 18, "status": "not_installed", "enabled": False, "category": "Administration", "ram_mb": 32, "cpu_pct": 1.2},
    {"id": "placement", "name": "Placement Portal", "icon": "💼", "version": "1.0.0", "size_mb": 28, "status": "not_installed", "enabled": False, "category": "Career", "ram_mb": 56, "cpu_pct": 2.0},
    {"id": "research", "name": "Research Portal", "icon": "🔬", "version": "1.0.0", "size_mb": 36, "status": "not_installed", "enabled": False, "category": "Research", "ram_mb": 72, "cpu_pct": 2.5},
]

UPDATES = [
    {"id": "UPT001", "package": "eduos-kernel", "version": "6.8.5", "type": "Security", "size_mb": 48, "critical": True, "status": "available", "desc": "Critical kernel security patch for CVE-2026-1234"},
    {"id": "UPT002", "package": "eduos-learn-hub", "version": "2.1.1", "type": "Bugfix", "size_mb": 12, "critical": False, "status": "available", "desc": "Fixed auto-save issue in exam mode"},
    {"id": "UPT003", "package": "eduos-cyber-lab", "version": "1.8.1", "type": "Enhancement", "size_mb": 24, "critical": False, "status": "available", "desc": "New lab: Web Application Security"},
    {"id": "UPT004", "package": "eduos-ui-framework", "version": "2.0.5", "type": "Feature", "size_mb": 8, "critical": False, "status": "available", "desc": "Glassmorphism theme improvements"},
    {"id": "UPT005", "package": "eduos-security-module", "version": "1.2.0", "type": "Security", "size_mb": 6, "critical": True, "status": "available", "desc": "Critical: Anti-cheat engine update"},
]

DEVICES = [
    {"id": "DEV0001", "name": "Lab-01-Desktop-01", "type": "Desktop", "dept": "CSE", "status": "online", "os": "EduOS 2.0", "ip": "10.0.1.10", "user": "student001", "last_seen": "2026-06-24 14:32"},
    {"id": "DEV0002", "name": "Lab-01-Desktop-02", "type": "Desktop", "dept": "CSE", "status": "online", "os": "EduOS 2.0", "ip": "10.0.1.11", "user": "student002", "last_seen": "2026-06-24 14:31"},
    {"id": "DEV0003", "name": "Library-Kiosk-01", "type": "Kiosk", "dept": "Library", "status": "online", "os": "EduOS 2.0", "ip": "10.0.3.5", "user": "library", "last_seen": "2026-06-24 14:30"},
    {"id": "DEV0004", "name": "Faculty-Laptop-DrSharma", "type": "Laptop", "dept": "ECE", "status": "online", "os": "EduOS 2.0", "ip": "10.0.2.20", "user": "faculty042", "last_seen": "2026-06-24 14:28"},
    {"id": "DEV0005", "name": "Server-Main-01", "type": "Server", "dept": "IT", "status": "online", "os": "EduOS Server 2.0", "ip": "10.0.0.2", "user": "admin", "last_seen": "2026-06-24 14:35"},
    {"id": "DEV0006", "name": "Lab-02-Desktop-15", "type": "Desktop", "dept": "IT", "status": "offline", "os": "EduOS 2.0", "ip": "10.0.1.25", "user": "student088", "last_seen": "2026-06-23 16:45"},
    {"id": "DEV0007", "name": "Smartboard-CLASS-A12", "type": "Smartboard", "dept": "ME", "status": "online", "os": "EduOS IoT 1.0", "ip": "10.0.4.12", "user": "lecture-hall", "last_seen": "2026-06-24 13:50"},
    {"id": "DEV0008", "name": "Admin-Terminal-01", "type": "Desktop", "dept": "Admin", "status": "online", "os": "EduOS 2.0", "ip": "10.0.0.10", "user": "admin", "last_seen": "2026-06-24 14:34"},
]


def generate_timeline(days=30):
    """Generate daily stats for the past N days."""
    data = []
    base_students = INSTITUTION["students"]
    base_devices = INSTITUTION["total_devices"]
    for i in range(days, 0, -1):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        data.append({
            "date": date,
            "active_students": int(base_students * (0.75 + random.random() * 0.2)),
            "online_devices": int(base_devices * (0.80 + random.random() * 0.15)),
            "exams_today": random.randint(2, 18),
            "avg_score": round(random.uniform(58, 82), 1),
            "system_health": round(random.uniform(94, 100), 1),
        })
    data.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "active_students": base_students,
        "online_devices": INSTITUTION["online_devices"],
        "exams_today": 12,
        "avg_score": 74.3,
        "system_health": 98.7,
    })
    return data


def generate_activity_log(count=50):
    actions = [
        "Student Enrolled", "Faculty Added", "Course Created", "Exam Scheduled",
        "Module Installed", "Module Enabled", "Update Installed", "Security Patch Applied",
        "Device Registered", "Device Disconnected", "Backup Completed", "System Health Check",
        "Lab Session Started", "Exam Submitted", "Result Published", "Attendance Synced",
        "Institution Settings Updated", "Branding Applied", "AI Query Processed",
    ]
    log = []
    for i in range(count):
        h = random.randint(0, 23)
        m = random.randint(0, 59)
        log.append({
            "timestamp": f"2026-06-{random.randint(10,24):02d}T{h:02d}:{m:02d}:00",
            "action": random.choice(actions),
            "details": f"Operation #{random.randint(10000, 99999)}"
        })
    return sorted(log, key=lambda x: x["timestamp"], reverse=True)


def generate_courses(count=20):
    subjects = [
        "Data Structures", "Algorithms", "Operating Systems", "Computer Networks",
        "Database Systems", "Machine Learning", "Web Development", "Cloud Computing",
        "Cyber Security", "Software Engineering", "Artificial Intelligence", "IoT",
        "Digital Electronics", "Control Systems", "Thermodynamics", "Fluid Mechanics",
        "Structural Analysis", "Financial Management", "Marketing", "Business Analytics",
    ]
    courses = []
    for i, subj in enumerate(subjects[:count], 1):
        courses.append({
            "id": f"CS{i:03d}", "name": subj,
            "dept": random.choice(DEPARTMENTS)["id"],
            "students": random.randint(40, 180),
            "progress": random.randint(30, 100),
            "active": random.random() > 0.15,
        })
    return courses


def generate_exams(count=15):
    types = ["Mid-Term", "Final", "Quiz", "Practical", "Viva"]
    exams = []
    for i in range(count):
        exam = {
            "id": f"EXM{i+1:03d}",
            "title": f"{random.choice(['CS', 'EC', 'ME', 'CE', 'IT'])} {random.randint(101, 501)} {random.choice(types)}",
            "dept": random.choice(DEPARTMENTS)["id"],
            "type": random.choice(types),
            "date": f"2026-{random.randint(3,7):02d}-{random.randint(10,28):02d}",
            "students": random.randint(30, 200),
            "submitted": 0,
            "avg_score": 0,
            "status": random.choice(["Scheduled", "Ongoing", "Completed", "Evaluated"]),
        }
        if exam["status"] in ("Completed", "Evaluated"):
            exam["submitted"] = exam["students"]
            exam["avg_score"] = round(random.uniform(45, 88), 1)
        elif exam["status"] == "Ongoing":
            exam["submitted"] = random.randint(exam["students"] // 2, exam["students"])
        exams.append(exam)
    return exams


def generate_system_health():
    return {
        "cpu_usage": round(random.uniform(25, 60), 1),
        "ram_usage": round(random.uniform(45, 75), 1),
        "disk_usage": round(random.uniform(55, 85), 1),
        "network_latency_ms": round(random.uniform(2, 15), 1),
        "uptime_days": 124,
        "services_running": 47,
        "services_total": 52,
        "last_backup": "2026-06-23 03:00 AM",
        "security_score": 96,
    }


def generate_all():
    data = {
        "institution": INSTITUTION,
        "departments": DEPARTMENTS,
        "modules": MODULES,
        "updates": UPDATES,
        "devices": DEVICES,
        "timeline": generate_timeline(),
        "activity": generate_activity_log(),
        "courses": generate_courses(),
        "exams": generate_exams(),
        "health": generate_system_health(),
    }
    with open(DATA_DIR / "ecosystem_data.json", "w") as f:
        json.dump(data, f, indent=2)
    return data


if __name__ == "__main__":
    generate_all()
    print("Demo data generated.")

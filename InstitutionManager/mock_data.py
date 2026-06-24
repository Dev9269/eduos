"""
EduOS Institution Manager — Mock Data Generator
Generates realistic sample data for demonstration and testing.
"""

import random
import json
from datetime import datetime, timedelta
from pathlib import Path
from config import save_json, PATHS

random.seed(42)

departments_data = [
    {"id": "CSE", "name": "Computer Science & Engineering", "hod": "Dr. Arvind Kumar", "estd": 2005, "students": 1200, "faculty": 45, "labs": 8},
    {"id": "ECE", "name": "Electronics & Communication", "hod": "Dr. Sunita Patel", "estd": 2004, "students": 980, "faculty": 38, "labs": 6},
    {"id": "ME", "name": "Mechanical Engineering", "hod": "Dr. Rajesh Singh", "estd": 2003, "students": 760, "faculty": 32, "labs": 5},
    {"id": "CE", "name": "Civil Engineering", "hod": "Dr. Priya Sharma", "estd": 2006, "students": 640, "faculty": 28, "labs": 4},
    {"id": "EE", "name": "Electrical Engineering", "hod": "Dr. Amit Verma", "estd": 2004, "students": 550, "faculty": 25, "labs": 4},
    {"id": "IT", "name": "Information Technology", "hod": "Dr. Neha Gupta", "estd": 2008, "students": 890, "faculty": 34, "labs": 6},
    {"id": "MBA", "name": "Master of Business Administration", "hod": "Dr. Rohit Mehta", "estd": 2010, "students": 420, "faculty": 18, "labs": 2},
    {"id": "BS", "name": "Basic Sciences", "hod": "Dr. Deepa Iyer", "estd": 2002, "students": 1500, "faculty": 55, "labs": 10},
]

first_names_f = ["Priya", "Ananya", "Divya", "Neha", "Riya", "Kavita", "Sneha", "Meera", "Pooja", "Isha",
                  "Shreya", "Anjali", "Nandini", "Varsha", "Tanya", "Kriti", "Aishwarya", "Shruti", "Bhavna", "Deepika"]
first_names_m = ["Arjun", "Rahul", "Amit", "Vivek", "Rohit", "Siddharth", "Karan", "Manish", "Harsh", "Aditya",
                 "Nikhil", "Vikram", "Sahil", "Aniket", "Pranav", "Kunal", "Dhruv", "Ravi", "Akash", "Yash"]
last_names = ["Sharma", "Verma", "Patel", "Singh", "Kumar", "Gupta", "Joshi", "Iyer", "Desai", "Reddy",
              "Nair", "Menon", "Rao", "Pillai", "Rajan", "Jain", "Agarwal", "Saxena", "Mishra", "Trivedi"]

subjects = [
    "Data Structures", "Algorithms", "Operating Systems", "Computer Networks", "Database Systems",
    "Software Engineering", "Machine Learning", "Artificial Intelligence", "Web Development", "Cloud Computing",
    "Cyber Security", "IoT", "Blockchain", "DevOps", "Mobile App Development",
    "Digital Electronics", "Microprocessors", "Control Systems", "Power Systems", "Signal Processing",
    "Thermodynamics", "Fluid Mechanics", "Strength of Materials", "Machine Design", "Manufacturing Science",
    "Structural Analysis", "Geotechnical Engineering", "Transportation Engineering", "Environmental Engineering", "Surveying",
    "Financial Management", "Marketing Management", "Human Resources", "Operations Research", "Business Analytics",
]

course_prefixes = {
    "CSE": ["CS", "AI", "DS", "SE"], "ECE": ["EC", "VL", "EM"], "ME": ["ME", "AE", "MP"],
    "CE": ["CE", "ST", "GE"], "EE": ["EE", "PS", "PE"], "IT": ["IT", "IS", "CC"],
    "MBA": ["MB", "FI", "HR", "MK"], "BS": ["PH", "CH", "MA", "BT"],
}


def generate_students(count=200):
    students = []
    dept_ids = [d["id"] for d in departments_data]
    years = [1, 2, 3, 4]
    for i in range(count):
        dept = random.choice(dept_ids)
        gender = random.choice(["M", "F"])
        first = random.choice(first_names_f if gender == "F" else first_names_m)
        last = random.choice(last_names)
        sem = random.choice(years)
        stu = {
            "id": f"STU{(i+1):04d}",
            "name": f"{first} {last}",
            "gender": gender,
            "department": dept,
            "year": sem,
            "semester": sem * 2 - random.choice([0, 1]),
            "email": f"{first.lower()}.{last.lower()}@institution.edu",
            "phone": f"+91-{random.randint(7000000000, 9999999999)}",
            "dob": f"{random.randint(1998, 2006)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            "address": f"{random.randint(1,999)} EduOS Street, Tech City",
            "cgpa": round(random.uniform(5.5, 9.8), 2),
            "attendance_pct": random.randint(65, 100),
            "status": random.choice(["Active", "Active", "Active", "Graduated", "Suspended"]),
            "enrolled_courses": random.sample(subjects, random.randint(4, 7)),
            "enrolled_date": f"2024-0{random.randint(6,8)}-{random.randint(10,28):02d}"
        }
        students.append(stu)
    return sorted(students, key=lambda s: s["id"])


def generate_faculty(count=60):
    faculty = []
    dept_ids = [d["id"] for d in departments_data]
    designations = ["Professor", "Associate Professor", "Assistant Professor", "Lecturer", "Dean", "HOD"]
    for i in range(count):
        dept = random.choice(dept_ids)
        gender = random.choice(["M", "F"])
        first = random.choice(first_names_f if gender == "F" else first_names_m)
        last = random.choice(last_names)
        desig = random.choice(designations)
        fac = {
            "id": f"FAC{(i+1):03d}",
            "name": f"Dr. {first} {last}",
            "gender": gender,
            "department": dept,
            "designation": desig,
            "qualification": random.choice(["Ph.D.", "Ph.D.", "Ph.D.", "M.Tech", "M.Sc", "MBA"]),
            "specialization": random.choice(subjects),
            "email": f"{first.lower()}.{last.lower()}@institution.edu",
            "phone": f"+91-{random.randint(7000000000, 9999999999)}",
            "experience_years": random.randint(2, 30),
            "courses_teaching": random.sample(subjects, random.randint(1, 4)),
            "status": "Active" if random.random() > 0.1 else "On Leave"
        }
        faculty.append(fac)
    return faculty


def generate_courses():
    courses = []
    idx = 1
    for dept in departments_data:
        prefixes = course_prefixes.get(dept["id"], ["XX"])
        num = random.randint(3, 6)
        for j in range(num):
            subj = random.choice(subjects)
            prefix = random.choice(prefixes)
            code = f"{prefix}{random.randint(100, 500)}"
            semesters = [s for s in range(1, 9)]
            courses.append({
                "id": code,
                "name": subj,
                "department": dept["id"],
                "credits": random.choice([2, 3, 3, 3, 4, 4]),
                "semester": random.choice(semesters),
                "faculty": "",
                "students_enrolled": random.randint(30, 120),
                "duration_weeks": 16,
                "type": random.choice(["Core", "Core", "Elective", "Lab", "Project"]),
                "description": f"A comprehensive course covering {subj.lower()} with practical applications."
            })
            idx += 1
    return courses


def generate_labs():
    lab_templates = [
        ("Computer Lab 1", "CSE", 60, ["Python", "Java", "C++", "Web Development"]),
        ("Computer Lab 2", "CSE", 60, ["AI/ML", "Data Science", "Cloud Computing"]),
        ("Computer Lab 3", "IT", 45, ["Networking", "Cyber Security", "Linux"]),
        ("Programming Lab", "CSE", 50, ["Algorithms", "Data Structures", "Competitive Programming"]),
        ("Electronics Lab", "ECE", 30, ["Digital Electronics", "Microcontrollers", "VLSI"]),
        ("Communication Lab", "ECE", 25, ["Signal Processing", "Communication Systems", "Embedded Systems"]),
        ("Mechanics Lab", "ME", 30, ["Thermodynamics", "Fluid Mechanics", "Strength of Materials"]),
        ("CAD/CAM Lab", "ME", 25, ["AutoCAD", "SolidWorks", "CNC Programming"]),
        ("Civil Materials Lab", "CE", 25, ["Concrete Technology", "Soil Mechanics", "Surveying"]),
        ("Electrical Machines Lab", "EE", 25, ["Power Systems", "Electrical Machines", "Control Systems"]),
        ("Physics Lab", "BS", 40, ["Optics", "Quantum Mechanics", "Electromagnetism"]),
        ("Chemistry Lab", "BS", 40, ["Organic Chemistry", "Analytical Chemistry", "Polymer Science"]),
        ("Robotics Lab", "CSE", 20, ["Robotics", "IoT", "Embedded Systems"]),
        ("Business Analytics Lab", "MBA", 35, ["Data Analytics", "Business Intelligence", "ERP"]),
    ]
    labs = []
    for i, (name, dept, capacity, tools) in enumerate(lab_templates, 1):
        labs.append({
            "id": f"LAB{i:02d}",
            "name": name,
            "department": dept,
            "capacity": capacity,
            "systems": capacity + random.randint(-5, 10),
            "tools": tools,
            "in_charge": f"Dr. {random.choice(first_names_m)} {random.choice(last_names)}",
            "status": random.choice(["Operational", "Operational", "Operational", "Maintenance", "Upgrading"]),
            "last_updated": f"2026-{random.randint(1,6):02d}-{random.randint(10,28):02d}"
        })
    return labs


def generate_exams():
    exam_types = ["Mid-Term", "Final", "Quiz", "Practical", "Viva"]
    exams = []
    for i in range(25):
        dept = random.choice(departments_data)
        subj = random.choice(subjects)
        etype = random.choice(exam_types)
        total = random.randint(30, 120)
        appeared = random.randint(int(total * 0.8), total)
        passed = random.randint(int(appeared * 0.6), appeared)
        exams.append({
            "id": f"EXM{i+1:03d}",
            "title": f"{subj} - {etype} Examination",
            "department": dept["id"],
            "subject": subj,
            "type": etype,
            "date": f"2026-{random.randint(3,7):02d}-{random.randint(10,28):02d}",
            "duration_minutes": random.choice([30, 45, 60, 90, 120, 180]),
            "total_students": total,
            "appeared": appeared,
            "passed": passed,
            "pass_rate": round((passed / appeared) * 100, 1) if appeared else 0,
            "avg_score": round(random.uniform(45, 85), 1),
            "highest": random.randint(85, 100),
            "lowest": random.randint(15, 40),
            "status": random.choice(["Scheduled", "Ongoing", "Completed", "Evaluated"])
        })
    return exams


def generate_devices():
    types = ["Desktop", "Laptop", "Tablet", "Smartboard", "Server", "Projector", "Printer", "Router"]
    statuses = ["Online", "Online", "Online", "Online", "Offline", "Maintenance"]
    devices = []
    for i in range(50):
        dtype = random.choice(types)
        dept = random.choice(departments_data)
        devices.append({
            "id": f"DEV{i+1:04d}",
            "name": f"{dtype} {random.choice(['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon'])}-{random.randint(100,999)}",
            "type": dtype,
            "department": dept["id"],
            "location": f"Block-{random.choice(['A','B','C','D','E'])} Floor {random.randint(1,5)}",
            "os": random.choice(["EduOS 2.0", "EduOS 1.9", "Windows 11", "Ubuntu 24.04", "macOS 15"]),
            "ip": f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
            "mac": ":".join([f"{random.randint(0,255):02X}" for _ in range(6)]),
            "status": random.choice(statuses),
            "last_seen": f"2026-06-{random.randint(10,24)} {random.randint(8,20):02d}:{random.randint(0,59):02d}",
            "assigned_to": random.choice(faculty_data)["name"] if 'faculty_data' in dir() else "IT Admin"
        })
    return devices


def generate_updates():
    import hashlib
    updates = []
    types = ["Security", "Feature", "Bugfix", "Enhancement", "Critical"]
    pkgs = ["eduos-kernel", "eduos-learn-hub", "eduos-exam-engine", "eduos-cyber-lab", "eduos-dev-suite",
            "eduos-security-module", "eduos-network-stack", "eduos-ui-framework", "eduos-ai-engine",
            "eduos-module-manager"]
    for i in range(15):
        pkg = random.choice(pkgs)
        ver = f"{random.randint(1,3)}.{random.randint(0,9)}.{random.randint(0,9)}"
        utype = random.choice(types)
        updates.append({
            "id": f"UPD{i+1:03d}",
            "package": pkg,
            "version": ver,
            "type": utype,
            "size_mb": random.randint(2, 250),
            "description": f"{utype} update for {pkg}: fixes and improvements",
            "release_date": f"2026-{random.randint(1,6):02d}-{random.randint(1,28):02d}",
            "status": random.choice(["Available", "Available", "Installed", "Pending", "Rolled Back"]),
            "devices_updated": random.randint(10, 500),
            "critical": utype == "Critical",
            "checksum": hashlib.sha256(pkg.encode()).hexdigest()[:16]
        })
    return updates


def generate_activity_log(entries=100):
    actions = [
        "Student Enrolled", "Faculty Added", "Course Created", "Exam Scheduled",
        "Module Installed", "Module Enabled", "Module Disabled", "Device Registered",
        "Update Installed", "Security Patch Applied", "Backup Completed", "System Health Check",
        "Lab Created", "Department Added", "Configuration Changed", "Data Exported",
        "User Login", "User Logout", "Password Changed", "Profile Updated"
    ]
    log = []
    for i in range(entries):
        day = random.randint(1, 24)
        hour = random.randint(6, 23)
        minute = random.randint(0, 59)
        action = random.choice(actions)
        log.append({
            "timestamp": f"2026-06-{day:02d}T{hour:02d}:{minute:02d}:00",
            "action": action,
            "details": f"{action} by admin — batch operation #{random.randint(1000, 9999)}"
        })
    return sorted(log, key=lambda x: x["timestamp"], reverse=True)


def generate_all():
    global faculty_data
    faculty_data = generate_faculty()
    students_data = generate_students()
    courses_data = generate_courses()
    labs_data = generate_labs()
    exams_data = generate_exams()
    devices_data = generate_devices()
    updates_data = generate_updates()
    activity_data = generate_activity_log()

    save_json(PATHS["departments"], departments_data)
    save_json(PATHS["courses"], courses_data)
    save_json(PATHS["students"], students_data)
    save_json(PATHS["faculty"], faculty_data)
    save_json(PATHS["labs"], labs_data)
    save_json(PATHS["exams"], exams_data)
    save_json(PATHS["devices"], devices_data)
    save_json(PATHS["updates"], updates_data)
    save_json(PATHS["activity"], activity_data)

    analytics = {
        "total_students": len(students_data),
        "total_faculty": len(faculty_data),
        "active_courses": len(courses_data),
        "total_exams": len(exams_data),
        "pass_rate": round(sum(e["pass_rate"] for e in exams_data) / len(exams_data), 1) if exams_data else 0,
        "avg_score": round(sum(e["avg_score"] for e in exams_data) / len(exams_data), 1) if exams_data else 0,
        "device_count": len(devices_data),
        "online_devices": sum(1 for d in devices_data if d["status"] == "Online"),
        "active_labs": sum(1 for l in labs_data if l["status"] == "Operational"),
        "storage_used_gb": 2846
    }
    save_json(PATHS["analytics"], analytics)

    total_students = sum(d["students"] for d in departments_data)
    total_faculty = sum(d["faculty"] for d in departments_data)
    total_labs = sum(d["labs"] for d in departments_data)
    cfg = {
        "name": "Parul University",
        "type": "University",
        "address": "Post Limda, Waghodia",
        "city": "Vadodara",
        "country": "India",
        "phone": "+91-2668-260301",
        "email": "info@paruluniversity.ac.in",
        "website": "https://www.paruluniversity.ac.in",
        "established": "2015",
        "accreditation": "NAAC A+",
        "principal": "Dr. Parul Shah",
        "student_count": total_students,
        "faculty_count": total_faculty,
        "departments": len(departments_data),
        "version": "2.0.0"
    }
    save_json(PATHS["institution"], cfg)

if __name__ == "__main__":
    generate_all()
    print("Mock data generated successfully.")

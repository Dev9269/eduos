#!/usr/bin/env python3
"""
EduOS Learn Hub - Student Learning Portal
Flask-based local web application for study materials, assignments, notes, and schedules.
"""

import sys
import os
import json
import sqlite3
import uuid
from datetime import datetime, date
from pathlib import Path

_ROOT_DIR = str(Path(__file__).resolve().parent.parent)
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from flask import (
    Flask,
    render_template_string,
    request,
    redirect,
    url_for,
    jsonify,
    session,
    send_from_directory,
    flash,
)
from design_system import (
    EduOSColors as C,
    apply_glass_theme,
    glass_card_style,
    glass_button_style,
    accent_glow_style,
    glass_success_button_style,
    glass_danger_button_style,
    glass_warning_button_style,
    status_badge_style,
    StatusBadge,
    SectionTitle,
    glass_stat_card_style,
    glass_banner_style,
)


DATA_DIR = Path.home() / ".eduos" / "learnhub"
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("EDUOS_FLASK_SECRET", os.urandom(32).hex())
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    )
    return response


BASE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EduOS Learn Hub</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',Inter,system-ui,sans-serif;background:#f1f5f9;color:#1e293b}}
.topbar{{background:linear-gradient(135deg,#1e3a5f,#2563eb);padding:16px 32px;display:flex;align-items:center;color:#fff;box-shadow:0 2px 12px rgba(0,0,0,.15)}}
.topbar h1{{font-size:22px;font-weight:600}}
.topbar .subtitle{{margin-left:16px;font-size:13px;opacity:.7}}
.topbar .user{{margin-left:auto;font-size:14px;opacity:.9}}
.container{{max-width:1200px;margin:0 auto;padding:24px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}}
.card{{background:#fff;border-radius:14px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,.06);transition:transform .2s,box-shadow .2s;cursor:pointer;border:1px solid #e8edf5}}
.card:hover{{transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,.1)}}
.card-icon{{font-size:36px;margin-bottom:12px}}
.card h3{{font-size:18px;margin-bottom:6px;color:#1e293b}}
.card p{{font-size:13px;color:#64748b;line-height:1.5}}
.card .count{{font-size:28px;font-weight:bold;color:#2563eb;margin:8px 0}}
.section{{margin-top:32px}}
.section h2{{font-size:20px;margin-bottom:16px;color:#334155}}
.list-card{{background:#fff;border-radius:10px;padding:16px 20px;border:1px solid #e8edf5;margin-bottom:8px;display:flex;align-items:center;gap:16px}}
.list-card .icon{{font-size:24px}}
.list-card .info{{flex:1}}
.list-card .info h4{{font-size:15px;color:#1e293b}}
.list-card .info p{{font-size:12px;color:#94a3b8}}
.list-card .badge{{padding:4px 12px;border-radius:20px;font-size:12px;background:#e0f2fe;color:#0369a1}}
.badge-pending{{background:#fef3c7;color:#b45309}}
.badge-done{{background:#dcfce7;color:#16a34a}}
.badge-submitted{{background:#dbeafe;color:#2563eb}}
.btn{{display:inline-block;padding:8px 20px;border-radius:8px;font-size:14px;font-weight:600;text-decoration:none;border:none;cursor:pointer;transition:opacity .2s}}
.btn:hover{{opacity:.85}}
.btn-primary{{background:#2563eb;color:#fff}}
.btn-success{{background:#16a34a;color:#fff}}
.btn-danger{{background:#dc2626;color:#fff}}
.btn-small{{padding:4px 12px;font-size:12px}}
.btn-warning{{background:#f59e0b;color:#fff}}
.form-group{{margin-bottom:16px}}
.form-group label{{display:block;font-size:14px;font-weight:600;margin-bottom:4px;color:#374151}}
.form-group input,.form-group textarea,.form-group select{{width:100%;padding:10px 14px;border:1px solid #d1d5db;border-radius:8px;font-size:14px;font-family:inherit}}
.form-group textarea{{min-height:120px;resize:vertical}}
.form-group input[type="file"]{{padding:8px}}
.page-title{{display:flex;align-items:center;gap:12px;margin-bottom:24px}}
.page-title h2{{font-size:24px;color:#1e293b}}
.page-title .back{{color:#2563eb;text-decoration:none;font-size:14px}}
.detail-card{{background:#fff;border-radius:12px;padding:24px;border:1px solid #e8edf5;margin-bottom:16px}}
.detail-card h3{{font-size:18px;margin-bottom:8px}}
.detail-card p{{font-size:14px;color:#475569;line-height:1.6}}
.detail-card .meta{{font-size:12px;color:#94a3b8;margin-top:8px}}
.detail-card hr{{margin:16px 0;border:none;border-top:1px solid #e8edf5}}
.flash{{padding:12px 20px;border-radius:8px;margin-bottom:16px;font-size:14px}}
.flash-success{{background:#dcfce7;color:#16a34a;border:1px solid #bbf7d0}}
.flash-error{{background:#fee2e2;color:#dc2626;border:1px solid #fecaca}}
.empty-state{{text-align:center;padding:48px;color:#94a3b8}}
.empty-state .icon{{font-size:48px;margin-bottom:12px}}
table{{width:100%;border-collapse:collapse;font-size:14px}}
th,td{{padding:12px 16px;text-align:left;border-bottom:1px solid #e8edf5}}
th{{background:#f8fafc;font-weight:600;color:#475569}}
.action-bar{{margin:16px 0;display:flex;gap:8px;flex-wrap:wrap}}
</style>
</head>
<body>
<div class="topbar">
<h1>\U0001f4da EduOS Learn Hub</h1>
<span class="subtitle">Student Learning Portal</span>
<span class="user">\U0001f464 {user}</span>
</div>
<div class="container">
"""

FOOTER = """
</div></body></html>"""


def flash_msg(category, text):
    return f'<div class="flash flash-{category}">{text}</div>'


def init_db():
    db_path = DATA_DIR / "learnhub.db"
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY, title TEXT, subject TEXT,
            description TEXT, file_path TEXT, uploaded DATE
        );
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY, title TEXT, subject TEXT,
            description TEXT, due DATE, done INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER, student TEXT, file_path TEXT,
            notes TEXT, submitted DATE, grade TEXT
        );
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT,
            created DATE, updated DATE
        );
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY, title TEXT, content TEXT,
            department TEXT, date DATE
        );
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY, title TEXT, type TEXT,
            datetime TEXT, location TEXT
        );
        INSERT OR IGNORE INTO assignments VALUES
            (1, 'Data Structures Assignment 3', 'CS201', 'Implement a binary search tree with insertion, deletion, and traversal operations.', '2026-06-20', 0),
            (2, 'Python Lab Report', 'CS101', 'Complete the lab exercise on functions and file handling. Include screenshots and code.', '2026-06-22', 0),
            (3, 'DBMS Project Proposal', 'CS301', 'Submit your database project proposal (1-2 pages) describing the problem statement, ER diagram, and proposed schema.', '2026-06-25', 1);
        INSERT OR IGNORE INTO announcements VALUES
            (1, 'Mid-Term Exam Schedule Released', 'The mid-term examination schedule is now available. Please check the timetable section for details. Exams will begin from July 1st.', 'Academic Affairs', '2026-06-14'),
            (2, 'Lab Maintenance Notice', 'Lab 2 will be closed for maintenance on June 18th. All scheduled lab sessions will be moved to Lab 4.', 'IT Department', '2026-06-13'),
            (3, 'Hackathon 2026 Registration Open', 'Register your team for the annual hackathon. Prizes worth ₹50,000. Last date: June 30th.', 'Student Affairs', '2026-06-12');
        INSERT OR IGNORE INTO schedule VALUES
            (1, 'Data Structures Lecture', 'class', '2026-06-15 09:00', 'Room 201'),
            (2, 'Python Programming Lab', 'lab', '2026-06-16 14:00', 'Lab 3'),
            (3, 'DBMS Tutorial', 'class', '2026-06-17 11:00', 'Room 105');
        INSERT OR IGNORE INTO materials VALUES
            (1, 'Introduction to Algorithms', 'CS201', 'Chapter 1: Algorithm Analysis - covers asymptotic notation, recurrence relations, and divide-and-conquer.', '', '2026-06-10'),
            (2, 'Python Programming Basics', 'CS101', 'Variables, loops, functions, and file handling. Beginner-friendly guide with examples.', '', '2026-06-08'),
            (3, 'Database Normalization', 'CS301', '1NF, 2NF, 3NF, BCNF explained with examples. Includes normalization exercises.', '', '2026-06-05');
        INSERT OR IGNORE INTO notes (id, title, content, created, updated) VALUES
            (1, 'Quick Reference: Big-O Notation', 'Common time complexities:\\n- O(1): Constant\\n- O(log n): Logarithmic\\n- O(n): Linear\\n- O(n log n): Linearithmic\\n- O(n²): Quadratic', '2026-06-10', '2026-06-10');
    """)
    conn.commit()
    conn.close()


@app.route("/")
def dashboard():
    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()
    materials = c.execute("SELECT COUNT(*) FROM materials").fetchone()[0]
    raw_assignments = c.execute(
        "SELECT * FROM assignments ORDER BY due LIMIT 5"
    ).fetchall()
    raw_announcements = c.execute(
        "SELECT * FROM announcements ORDER BY date DESC LIMIT 5"
    ).fetchall()
    notes_c = c.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    schedule_c = c.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]
    assignments_c = c.execute("SELECT COUNT(*) FROM assignments").fetchone()[0]
    announcements_c = c.execute("SELECT COUNT(*) FROM announcements").fetchone()[0]
    conn.close()

    user = os.environ.get("USER", "Student")

    # Build assignment cards
    assignment_html = ""
    for a in raw_assignments:
        status_badge = "done" if a[5] else "pending"
        status_text = "Completed" if a[5] else "Pending"
        icon = "✅" if a[5] else "⏳"
        assignment_html += f"""
        <div class="list-card">
            <div class="icon">{icon}</div>
            <div class="info">
                <h4>{a[1]}</h4>
                <p>Due: {a[4]} | {a[2]}</p>
            </div>
            <span class="badge badge-{status_badge}">{status_text}</span>
            <a href="/assignments/{a[0]}" class="btn btn-primary btn-small">View</a>
        </div>"""

    # Build announcement cards
    ann_html = ""
    for a in raw_announcements:
        ann_html += f"""
        <div class="list-card">
            <div class="icon">📢</div>
            <div class="info">
                <h4>{a[1]}</h4>
                <p>{a[4]} | {a[3]}</p>
            </div>
            <a href="/announcements/{a[0]}" class="btn btn-primary btn-small">Read</a>
        </div>"""

    if not assignment_html:
        assignment_html = '<div class="empty-state"><div class="icon">📝</div><p>No assignments yet</p></div>'
    if not ann_html:
        ann_html = '<div class="empty-state"><div class="icon">📢</div><p>No announcements</p></div>'

    body = f"""
    <div class="grid">
        <div class="card" onclick="window.location='/materials'">
            <div class="card-icon">📖</div>
            <h3>Study Materials</h3>
            <div class="count">{materials}</div>
            <p>Course notes, textbooks, and reference materials</p>
        </div>
        <div class="card" onclick="window.location='/assignments'">
            <div class="card-icon">📝</div>
            <h3>Assignments</h3>
            <div class="count">{assignments_c}</div>
            <p>Pending and completed assignments</p>
        </div>
        <div class="card" onclick="window.location='/schedule'">
            <div class="card-icon">📅</div>
            <h3>Schedule</h3>
            <div class="count">{schedule_c}</div>
            <p>Classes, exams, and events timetable</p>
        </div>
        <div class="card" onclick="window.location='/notes'">
            <div class="card-icon">✏️</div>
            <h3>My Notes</h3>
            <div class="count">{notes_c}</div>
            <p>Personal notes and annotations</p>
        </div>
        <div class="card" onclick="window.location='/announcements'">
            <div class="card-icon">📢</div>
            <h3>Announcements</h3>
            <div class="count">{announcements_c}</div>
            <p>Institution and department updates</p>
        </div>
        <div class="card" onclick="window.location='/timetable'">
            <div class="card-icon">🗓️</div>
            <h3>Timetable</h3>
            <div class="count">{schedule_c}</div>
            <p>Your weekly class schedule</p>
        </div>
    </div>
    <div class="section"><h2>📋 Recent Assignments</h2>{assignment_html}</div>
    <div class="section"><h2>📢 Latest Announcements</h2>{ann_html}</div>"""

    return BASE.format(user=user) + body + FOOTER


@app.route("/assignments")
def assignments_page():
    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()
    items = c.execute("SELECT * FROM assignments ORDER BY due").fetchall()
    conn.close()

    user = os.environ.get("USER", "Student")
    rows = ""
    for i in items:
        status = "✅ Completed" if i[5] else "⏳ Pending"
        badge = "badge-done" if i[5] else "badge-pending"
        desc = i[3][:100] + ("..." if len(i[3]) > 100 else "")
        rows += f"""
        <div class="list-card">
            <div class="icon">{"✅" if i[5] else "⏳"}</div>
            <div class="info">
                <h4>{i[1]}</h4>
                <p>{desc} | Due: {i[4]}</p>
            </div>
            <span class="badge {badge}">{status}</span>
            <a href="/assignments/{i[0]}" class="btn btn-primary btn-small">View</a>
        </div>"""

    if not rows:
        rows = '<div class="empty-state"><div class="icon">📝</div><p>No assignments yet</p></div>'

    body = f"""
    <div class="page-title"><a href="/" class="back">← Back to Dashboard</a></div>
    <h2>📝 Assignments</h2>
    {rows}"""

    return BASE.format(user=user) + body + FOOTER


@app.route("/assignments/<int:aid>")
def assignment_detail(aid):
    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()
    item = c.execute("SELECT * FROM assignments WHERE id=?", (aid,)).fetchone()
    submissions = c.execute(
        "SELECT * FROM submissions WHERE assignment_id=? ORDER BY submitted DESC",
        (aid,),
    ).fetchall()
    conn.close()

    if not item:
        return redirect("/assignments")

    user = os.environ.get("USER", "student")
    has_submitted = any(s[2] == user for s in submissions)
    status_text = "✅ Completed" if item[5] else "⏳ Pending"

    # Submissions table
    sub_rows = ""
    for s in submissions:
        grade = s[6] if s[6] else "Not graded"
        filename = Path(s[3]).name
        sub_rows += f"<tr><td>{s[2]}</td><td>{s[5]}</td><td><a href='/uploads/{filename}' style='color:#2563eb'>Download</a></td><td>{grade}</td></tr>"

    flash_msg_html = ""
    if request.args.get("submitted"):
        flash_msg_html = flash_msg("success", "✅ Assignment submitted successfully!")
    elif request.args.get("error"):
        flash_msg_html = flash_msg("error", "❌ Submission failed. Please try again.")

    alert_html = ""
    if has_submitted:
        alert_html = '<p style="color:#16a34a;">✅ You have already submitted this assignment. Upload again to update your submission.</p>'

    body = f'''
    <div class="page-title"><a href="/assignments" class="back">← Back to Assignments</a></div>
    {flash_msg_html}
    <div class="detail-card">
        <h3>{item[1]}</h3>
        <p><strong>Subject:</strong> {item[2]}</p>
        <p><strong>Due Date:</strong> {item[4]}</p>
        <p><strong>Status:</strong> {status_text}</p>
        <hr>
        <p>{item[3]}</p>
    </div>
    <div class="detail-card">
        <h3>📤 Submit Assignment</h3>
        {alert_html}
        <form method="POST" enctype="multipart/form-data" action="/assignments/{aid}/submit">
            <div class="form-group">
                <label>Your Name</label>
                <input type="text" name="student_name" value="{user}" required>
            </div>
            <div class="form-group">
                <label>Upload File (PDF, ZIP, PY, JAVA, DOC)</label>
                <input type="file" name="file" required>
            </div>
            <div class="form-group">
                <label>Notes (optional)</label>
                <textarea name="notes" placeholder="Add any notes about your submission..."></textarea>
            </div>
            <button type="submit" class="btn btn-success">📤 Submit Assignment</button>
        </form>
    </div>'''

    if sub_rows:
        body += f"""
        <div class="detail-card">
            <h3>📋 Submissions</h3>
            <table><tr><th>Student</th><th>Date</th><th>File</th><th>Grade</th></tr>
            {sub_rows}</table>
        </div>"""

    return BASE.format(user=user) + body + FOOTER


@app.route("/assignments/<int:aid>/submit", methods=["POST"])
def submit_assignment(aid):
    student_name = request.form.get("student_name", "unknown")
    notes = request.form.get("notes", "")

    if "file" not in request.files:
        return redirect(f"/assignments/{aid}?error=1")

    f = request.files["file"]
    if f.filename == "":
        return redirect(f"/assignments/{aid}?error=1")

    ext = Path(f.filename).suffix
    safe_name = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / safe_name
    f.save(str(file_path))

    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()
    c.execute(
        "INSERT INTO submissions (assignment_id, student, file_path, notes, submitted) VALUES (?, ?, ?, ?, ?)",
        (aid, student_name, str(file_path), notes, date.today().isoformat()),
    )
    conn.commit()
    conn.close()

    return redirect(f"/assignments/{aid}?submitted=1")


@app.route("/schedule")
def schedule_page():
    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()
    items = c.execute("SELECT * FROM schedule ORDER BY datetime").fetchall()
    conn.close()

    user = os.environ.get("USER", "Student")
    rows = ""
    for i in items:
        icon = "📚" if i[2] == "class" else "💻"
        rows += f"""
        <div class="list-card">
            <div class="icon">{icon}</div>
            <div class="info"><h4>{i[1]}</h4><p>{i[3]} | {i[4]}</p></div>
            <span class="badge">{i[2].capitalize()}</span>
        </div>"""
    if not rows:
        rows = '<div class="empty-state"><div class="icon">📅</div><p>No schedule items</p></div>'

    body = f"""
    <div class="page-title"><a href="/" class="back">← Back to Dashboard</a></div>
    <h2>📅 Schedule</h2>
    {rows}"""

    return BASE.format(user=user) + body + FOOTER


@app.route("/materials")
def materials_page():
    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()
    items = c.execute("SELECT * FROM materials").fetchall()
    conn.close()

    user = os.environ.get("USER", "Student")
    rows = ""
    for i in items:
        desc = i[3][:150] + ("..." if len(i[3]) > 150 else "")
        rows += f"""
        <div class="list-card">
            <div class="icon">📘</div>
            <div class="info">
                <h4>{i[1]}</h4>
                <p>{i[2]}: {desc}</p>
                <p style="font-size:12px;color:#94a3b8;">Uploaded: {i[5]}</p>
            </div>
        </div>"""
    if not rows:
        rows = '<div class="empty-state"><div class="icon">📖</div><p>No materials available</p></div>'

    body = f"""
    <div class="page-title"><a href="/" class="back">← Back to Dashboard</a></div>
    <h2>📖 Study Materials</h2>
    {rows}"""

    return BASE.format(user=user) + body + FOOTER


@app.route("/notes")
def notes_page():
    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()
    items = c.execute("SELECT * FROM notes ORDER BY updated DESC").fetchall()
    conn.close()

    user = os.environ.get("USER", "Student")
    rows = ""
    for i in items:
        content_preview = i[2][:150] + ("..." if len(i[2]) > 150 else "")
        rows += f"""
        <div class="list-card">
            <div class="icon">📄</div>
            <div class="info">
                <h4>{i[1]}</h4>
                <p>{content_preview}</p>
                <p style="font-size:12px;color:#94a3b8;">Updated: {i[4]}</p>
            </div>
            <a href="/notes/{i[0]}" class="btn btn-primary btn-small">View</a>
            <a href="/notes/{i[0]}/edit" class="btn btn-warning btn-small">Edit</a>
            <a href="/notes/{i[0]}/delete" class="btn btn-danger btn-small" onclick="return confirm('Delete this note?')">Del</a>
        </div>"""

    if not rows:
        rows = '<div class="empty-state"><div class="icon">✏️</div><p>No notes yet. Create your first note!</p></div>'

    # Check for flash messages
    flash_messages = ""
    if request.args.get("saved"):
        flash_messages = flash_msg("success", "✅ Note saved successfully!")
    elif request.args.get("deleted"):
        flash_messages = flash_msg("success", "🗑 Note deleted successfully!")

    body = f"""
    <div class="page-title"><a href="/" class="back">← Back to Dashboard</a></div>
    <h2>✏️ My Notes</h2>
    {flash_messages}
    <div class="action-bar"><a href="/notes/new" class="btn btn-primary">➕ Create Note</a></div>
    {rows}"""

    return BASE.format(user=user) + body + FOOTER


@app.route("/notes/new", methods=["GET", "POST"])
def notes_new():
    user = os.environ.get("USER", "Student")

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        today = date.today().isoformat()
        conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
        c = conn.cursor()
        c.execute(
            "INSERT INTO notes (title, content, created, updated) VALUES (?, ?, ?, ?)",
            (title, content, today, today),
        )
        conn.commit()
        conn.close()
        return redirect("/notes?saved=1")

    body = f"""
    <div class="page-title"><a href="/notes" class="back">← Back to Notes</a></div>
    <h2>➕ Create Note</h2>
    <div class="detail-card">
        <form method="POST">
            <div class="form-group">
                <label>Title</label>
                <input type="text" name="title" required placeholder="Note title">
            </div>
            <div class="form-group">
                <label>Content</label>
                <textarea name="content" required placeholder="Write your note here..."></textarea>
            </div>
            <button type="submit" class="btn btn-success">💾 Save Note</button>
        </form>
    </div>"""

    return BASE.format(user=user) + body + FOOTER


@app.route("/notes/<int:nid>")
def notes_view(nid):
    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()
    item = c.execute("SELECT * FROM notes WHERE id=?", (nid,)).fetchone()
    conn.close()

    if not item:
        return redirect("/notes")

    user = os.environ.get("USER", "Student")
    body = f"""
    <div class="page-title"><a href="/notes" class="back">← Back to Notes</a></div>
    <div class="detail-card">
        <h3>{item[1]}</h3>
        <p style="white-space: pre-wrap;">{item[2]}</p>
        <div class="meta">Created: {item[3]} | Updated: {item[4]}</div>
    </div>
    <div class="action-bar">
        <a href="/notes/{nid}/edit" class="btn btn-primary">✏️ Edit</a>
        <a href="/notes/{nid}/delete" class="btn btn-danger" onclick="return confirm('Delete this note?')">🗑 Delete</a>
    </div>"""

    return BASE.format(user=user) + body + FOOTER


@app.route("/notes/<int:nid>/edit", methods=["GET", "POST"])
def notes_edit(nid):
    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()
    item = c.execute("SELECT * FROM notes WHERE id=?", (nid,)).fetchone()

    if not item:
        conn.close()
        return redirect("/notes")

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        today = date.today().isoformat()
        c.execute(
            "UPDATE notes SET title=?, content=?, updated=? WHERE id=?",
            (title, content, today, nid),
        )
        conn.commit()
        conn.close()
        return redirect(f"/notes/{nid}")

    conn.close()

    user = os.environ.get("USER", "Student")
    body = f'''
    <div class="page-title"><a href="/notes" class="back">← Back to Notes</a></div>
    <h2>✏️ Edit Note</h2>
    <div class="detail-card">
        <form method="POST">
            <div class="form-group">
                <label>Title</label>
                <input type="text" name="title" value="{item[1]}" required>
            </div>
            <div class="form-group">
                <label>Content</label>
                <textarea name="content" required>{item[2]}</textarea>
            </div>
            <button type="submit" class="btn btn-success">💾 Save Changes</button>
        </form>
    </div>'''

    return BASE.format(user=user) + body + FOOTER


@app.route("/notes/<int:nid>/delete")
def notes_delete(nid):
    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id=?", (nid,))
    conn.commit()
    conn.close()
    return redirect("/notes?deleted=1")


@app.route("/announcements")
def announcements_full():
    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()
    items = c.execute("SELECT * FROM announcements ORDER BY date DESC").fetchall()
    conn.close()

    user = os.environ.get("USER", "Student")
    rows = ""
    for i in items:
        desc = i[2][:150] + ("..." if len(i[2]) > 150 else "")
        rows += f"""
        <div class="list-card">
            <div class="icon">📢</div>
            <div class="info">
                <h4>{i[1]}</h4>
                <p>{desc}</p>
                <p style="font-size:12px;color:#94a3b8;">{i[4]} | {i[3]}</p>
            </div>
            <a href="/announcements/{i[0]}" class="btn btn-primary btn-small">Read</a>
        </div>"""
    if not rows:
        rows = '<div class="empty-state"><div class="icon">📢</div><p>No announcements</p></div>'

    body = f"""
    <div class="page-title"><a href="/" class="back">← Back to Dashboard</a></div>
    <h2>📢 Announcements</h2>
    {rows}"""

    return BASE.format(user=user) + body + FOOTER


@app.route("/announcements/<int:aid>")
def announcement_detail(aid):
    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()
    item = c.execute("SELECT * FROM announcements WHERE id=?", (aid,)).fetchone()
    conn.close()

    if not item:
        return redirect("/announcements")

    user = os.environ.get("USER", "Student")
    body = f"""
    <div class="page-title"><a href="/announcements" class="back">← Back to Announcements</a></div>
    <div class="detail-card">
        <h3>{item[1]}</h3>
        <p>{item[2]}</p>
        <div class="meta">{item[4]} | {item[3]}</div>
    </div>"""

    return BASE.format(user=user) + body + FOOTER


@app.route("/timetable")
def timetable_page():
    return schedule_page()


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(str(UPLOAD_DIR), filename)


@app.route("/api/stats")
def api_stats():
    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()
    data = {
        "materials": c.execute("SELECT COUNT(*) FROM materials").fetchone()[0],
        "assignments": c.execute("SELECT COUNT(*) FROM assignments").fetchone()[0],
        "notes": c.execute("SELECT COUNT(*) FROM notes").fetchone()[0],
        "announcements": c.execute("SELECT COUNT(*) FROM announcements").fetchone()[0],
        "schedule": c.execute("SELECT COUNT(*) FROM schedule").fetchone()[0],
        "submissions": c.execute("SELECT COUNT(*) FROM submissions").fetchone()[0],
    }
    conn.close()
    return jsonify(data)


def main():
    init_db()
    print("\n" + "=" * 50)
    print("  📚 EduOS Learn Hub - Student Learning Portal")
    print("  Running at: http://localhost:5050")
    print("  Press Ctrl+C to stop")
    print("=" * 50 + "\n")
    app.run(host="127.0.0.1", port=5050, debug=False)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
EduOS Learn Hub - Student Learning Portal
Flask-based local web application for study materials, assignments, notes, and schedules.
"""

import sys
import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template_string, request, redirect, url_for, jsonify, session, send_from_directory


DATA_DIR = Path.home() / ".eduos" / "learnhub"
DATA_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.secret_key = "eduos-learnhub-secret-key-2026"


HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>EduOS Learn Hub</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Inter, system-ui, -apple-system, sans-serif;
            background: #f1f5f9; color: #1e293b;
        }
        .topbar {
            background: linear-gradient(135deg, #1e3a5f, #2563eb);
            padding: 16px 32px; display: flex; align-items: center;
            color: white; box-shadow: 0 2px 12px rgba(0,0,0,0.15);
        }
        .topbar h1 { font-size: 22px; font-weight: 600; }
        .topbar .subtitle { margin-left: 16px; font-size: 13px; opacity: 0.7; }
        .topbar .user { margin-left: auto; font-size: 14px; opacity: 0.9; }
        .container { max-width: 1200px; margin: 0 auto; padding: 24px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
        .card {
            background: white; border-radius: 14px; padding: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer; border: 1px solid #e8edf5;
        }
        .card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }
        .card-icon { font-size: 36px; margin-bottom: 12px; }
        .card h3 { font-size: 18px; margin-bottom: 6px; color: #1e293b; }
        .card p { font-size: 13px; color: #64748b; line-height: 1.5; }
        .card .count { font-size: 28px; font-weight: bold; color: #2563eb; margin: 8px 0; }
        .section { margin-top: 32px; }
        .section h2 { font-size: 20px; margin-bottom: 16px; color: #334155; }
        .list-card {
            background: white; border-radius: 10px; padding: 16px 20px;
            border: 1px solid #e8edf5; margin-bottom: 8px;
            display: flex; align-items: center; gap: 16px;
        }
        .list-card .icon { font-size: 24px; }
        .list-card .info { flex: 1; }
        .list-card .info h4 { font-size: 15px; color: #1e293b; }
        .list-card .info p { font-size: 12px; color: #94a3b8; }
        .list-card .badge {
            padding: 4px 12px; border-radius: 20px; font-size: 12px;
            background: #e0f2fe; color: #0369a1;
        }
        .badge-pending { background: #fef3c7; color: #b45309; }
        .badge-done { background: #dcfce7; color: #16a34a; }
        @media (max-width: 768px) {
            .container { padding: 16px; }
            .topbar { padding: 12px 16px; flex-wrap: wrap; }
        }
    </style>
</head>
<body>
    <div class="topbar">
        <h1>📚 EduOS Learn Hub</h1>
        <span class="subtitle">Student Learning Portal</span>
        <span class="user">👤 {{ user }}</span>
    </div>
    <div class="container">
        <div class="grid">
            <div class="card" onclick="window.location='/materials'">
                <div class="card-icon">📖</div>
                <h3>Study Materials</h3>
                <div class="count">{{ materials_count }}</div>
                <p>Course notes, textbooks, and reference materials</p>
            </div>
            <div class="card" onclick="window.location='/assignments'">
                <div class="card-icon">📝</div>
                <h3>Assignments</h3>
                <div class="count">{{ assignments_count }}</div>
                <p>Pending and completed assignments</p>
            </div>
            <div class="card" onclick="window.location='/schedule'">
                <div class="card-icon">📅</div>
                <h3>Schedule</h3>
                <div class="count">{{ schedule_count }}</div>
                <p>Classes, exams, and events timetable</p>
            </div>
            <div class="card" onclick="window.location='/notes'">
                <div class="card-icon">✏️</div>
                <h3>My Notes</h3>
                <div class="count">{{ notes_count }}</div>
                <p>Personal notes and annotations</p>
            </div>
            <div class="card" onclick="window.location='/announcements'">
                <div class="card-icon">📢</div>
                <h3>Announcements</h3>
                <div class="count">{{ announcements_count }}</div>
                <p>Institution and department updates</p>
            </div>
            <div class="card" onclick="window.location='/timetable'">
                <div class="card-icon">🗓️</div>
                <h3>Timetable</h3>
                <div class="count">{{ timetable_count }}</div>
                <p>Your weekly class schedule</p>
            </div>
        </div>

        <div class="section">
            <h2>📋 Recent Assignments</h2>
            {% for a in assignments %}
            <div class="list-card">
                <div class="icon">📄</div>
                <div class="info">
                    <h4>{{ a.title }}</h4>
                    <p>Due: {{ a.due }} | {{ a.subject }}</p>
                </div>
                <span class="badge badge-{{ 'done' if a.done else 'pending' }}">{{ '✅ Completed' if a.done else '⏳ Pending' }}</span>
            </div>
            {% endfor %}
        </div>

        <div class="section">
            <h2>📢 Latest Announcements</h2>
            {% for a in announcements %}
            <div class="list-card">
                <div class="icon">📢</div>
                <div class="info">
                    <h4>{{ a.title }}</h4>
                    <p>{{ a.date }} | {{ a.department }}</p>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""


def init_db():
    db_path = DATA_DIR / "learnhub.db"
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY, title TEXT, subject TEXT,
            description TEXT, file_path TEXT, uploaded DATE
        );
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY, title TEXT, subject TEXT,
            description TEXT, due DATE, done INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY, title TEXT, content TEXT,
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
            (1, 'Data Structures Assignment 3', 'CS201', 'Implement a binary search tree', '2026-06-20', 0),
            (2, 'Python Lab Report', 'CS101', 'Complete the lab exercise on functions', '2026-06-22', 0),
            (3, 'DBMS Project Proposal', 'CS301', 'Submit your database project proposal', '2026-06-25', 1);

        INSERT OR IGNORE INTO announcements VALUES
            (1, 'Mid-Term Exam Schedule Released', 'The mid-term examination schedule is now available.', 'Academic Affairs', '2026-06-14'),
            (2, 'Lab Maintenance Notice', 'Lab 2 will be closed for maintenance on June 18th.', 'IT Department', '2026-06-13'),
            (3, 'Hackathon 2026 Registration Open', 'Register your team for the annual hackathon.', 'Student Affairs', '2026-06-12');

        INSERT OR IGNORE INTO schedule VALUES
            (1, 'Data Structures Lecture', 'class', '2026-06-15 09:00', 'Room 201'),
            (2, 'Python Programming Lab', 'lab', '2026-06-16 14:00', 'Lab 3'),
            (3, 'DBMS Tutorial', 'class', '2026-06-17 11:00', 'Room 105');

        INSERT OR IGNORE INTO materials VALUES
            (1, 'Introduction to Algorithms', 'CS201', 'Chapter 1: Algorithm Analysis', '', '2026-06-10'),
            (2, 'Python Programming Basics', 'CS101', 'Variables, loops, and functions', '', '2026-06-08'),
            (3, 'Database Normalization', 'CS301', '1NF, 2NF, 3NF, and BCNF', '', '2026-06-05');
    ''')
    conn.commit()
    conn.close()


@app.route('/')
def dashboard():
    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()

    materials = c.execute("SELECT COUNT(*) FROM materials").fetchone()[0]
    assignments = c.execute("SELECT * FROM assignments ORDER BY due").fetchall()
    announcements = c.execute("SELECT * FROM announcements ORDER BY date DESC").fetchall()
    notes_c = c.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    schedule_c = c.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]
    assignments_c = c.execute("SELECT COUNT(*) FROM assignments").fetchone()[0]
    announcements_c = c.execute("SELECT COUNT(*) FROM announcements").fetchone()[0]

    conn.close()

    return render_template_string(
        HTML_TEMPLATE,
        user=os.environ.get('USER', 'Student'),
        materials_count=materials,
        assignments_count=assignments_c,
        schedule_count=schedule_c,
        notes_count=notes_c,
        announcements_count=announcements_c,
        timetable_count=schedule_c,
        assignments=[{
            'title': a[1], 'subject': a[2],
            'due': a[4], 'done': bool(a[5])
        } for a in assignments[:5]],
        announcements=[{
            'title': a[1], 'department': a[3], 'date': a[4]
        } for a in announcements[:5]]
    )


@app.route('/assignments')
def assignments_page():
    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()
    items = c.execute("SELECT * FROM assignments ORDER BY due").fetchall()
    conn.close()
    html = "<html><head><title>Assignments</title><style>"
    html += "body{font-family:system-ui;background:#f1f5f9;padding:32px;max-width:800px;margin:auto}"
    html += "h1{color:#1e293b}.item{background:white;padding:16px;border-radius:8px;margin:8px 0;border:1px solid #e8edf5}"
    html += "</style></head><body><h1>📝 Assignments</h1><a href='/' style='color:#2563eb'>← Back</a>"
    for i in items:
        status = "✅ Completed" if i[5] else "⏳ Pending"
        html += f"<div class='item'><h3>{i[1]}</h3><p>{i[3]}</p><p>Due: {i[4]} | {i[2]} | {status}</p></div>"
    html += "</body></html>"
    return html


@app.route('/schedule')
def schedule_page():
    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()
    items = c.execute("SELECT * FROM schedule ORDER BY datetime").fetchall()
    conn.close()
    html = "<html><head><title>Schedule</title><style>"
    html += "body{font-family:system-ui;background:#f1f5f9;padding:32px;max-width:800px;margin:auto}"
    html += "h1{color:#1e293b}.item{background:white;padding:16px;border-radius:8px;margin:8px 0;border:1px solid #e8edf5}"
    html += "</style></head><body><h1>📅 Schedule</h1><a href='/' style='color:#2563eb'>← Back</a>"
    for i in items:
        icon = "📚" if i[2] == "class" else "💻"
        html += f"<div class='item'><h3>{icon} {i[1]}</h3><p>{i[3]} | {i[4]}</p></div>"
    html += "</body></html>"
    return html


@app.route('/materials')
def materials_page():
    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()
    items = c.execute("SELECT * FROM materials").fetchall()
    conn.close()
    html = "<html><head><title>Study Materials</title><style>"
    html += "body{font-family:system-ui;background:#f1f5f9;padding:32px;max-width:800px;margin:auto}"
    html += "h1{color:#1e293b}.item{background:white;padding:16px;border-radius:8px;margin:8px 0;border:1px solid #e8edf5}"
    html += "</style></head><body><h1>📖 Study Materials</h1><a href='/' style='color:#2563eb'>← Back</a>"
    for i in items:
        html += f"<div class='item'><h3>{i[1]}</h3><p>{i[2]}: {i[3]}</p><p>Uploaded: {i[5]}</p></div>"
    html += "</body></html>"
    return html


@app.route('/notes')
def notes_page():
    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()
    items = c.execute("SELECT * FROM notes").fetchall()
    conn.close()
    html = "<html><head><title>My Notes</title><style>"
    html += "body{font-family:system-ui;background:#f1f5f9;padding:32px;max-width:800px;margin:auto}"
    html += "h1{color:#1e293b}.item{background:white;padding:16px;border-radius:8px;margin:8px 0;border:1px solid #e8edf5}"
    html += "</style></head><body><h1>✏️ My Notes</h1><a href='/' style='color:#2563eb'>← Back</a>"
    for i in items:
        html += f"<div class='item'><h3>{i[1]}</h3><p>{i[2][:200]}...</p></div>"
    html += "</body></html>"
    return html


@app.route('/announcements')
def announcements_full():
    conn = sqlite3.connect(str(DATA_DIR / "learnhub.db"))
    c = conn.cursor()
    items = c.execute("SELECT * FROM announcements ORDER BY date DESC").fetchall()
    conn.close()
    html = "<html><head><title>Announcements</title><style>"
    html += "body{font-family:system-ui;background:#f1f5f9;padding:32px;max-width:800px;margin:auto}"
    html += "h1{color:#1e293b}.item{background:white;padding:16px;border-radius:8px;margin:8px 0;border:1px solid #e8edf5}"
    html += "</style></head><body><h1>📢 Announcements</h1><a href='/' style='color:#2563eb'>← Back</a>"
    for i in items:
        html += f"<div class='item'><h3>{i[1]}</h3><p>{i[2]}</p><p>{i[4]} | {i[3]}</p></div>"
    html += "</body></html>"
    return html


@app.route('/timetable')
def timetable_page():
    return schedule_page()


def main():
    init_db()
    print("\n" + "="*50)
    print("  📚 EduOS Learn Hub - Student Learning Portal")
    print("  Running at: http://localhost:5050")
    print("  Press Ctrl+C to stop")
    print("="*50 + "\n")
    app.run(host="127.0.0.1", port=5050, debug=False)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""EduOS Welcome — First-run experience shown on first login"""

import sys, os
from pathlib import Path

WELCOME_FLAG = Path.home() / ".eduos-welcome-done"

def main():
    # Only show once
    if WELCOME_FLAG.exists():
        sys.exit(0)

    try:
        from PyQt6.QtWidgets import (
            QApplication, QWizard, QWizardPage, QVBoxLayout,
            QLabel, QCheckBox, QPushButton
        )
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont
    except ImportError:
        # PyQt6 not available — mark as done and exit
        WELCOME_FLAG.touch()
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setApplicationName("EduOS Welcome")

    wizard = QWizard()
    wizard.setWindowTitle("Welcome to EduOS")
    wizard.setFixedSize(700, 500)
    wizard.setWizardStyle(QWizard.WizardStyle.ModernStyle)
    wizard.setStyleSheet("""
        QWizard { background: #0A1628; color: #E8F0FE; }
        QWizard QLabel { color: #E8F0FE; }
        QPushButton {
            background: #4A9EFF; color: white;
            border-radius: 6px; padding: 8px 20px;
            font-weight: bold;
        }
        QPushButton:hover { background: #3B82F6; }
    """)

    # Page 1: Welcome
    page1 = QWizardPage()
    page1.setTitle("Welcome to EduOS")
    layout1 = QVBoxLayout(page1)
    title = QLabel("🎓 EduOS")
    title.setStyleSheet("font-size: 56px; font-weight: bold; color: #4A9EFF;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout1.addWidget(title)
    sub = QLabel("Engineering Education Platform\nPowered by FreeBSD")
    sub.setStyleSheet("font-size: 16px; color: #8BA3C0;")
    sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout1.addWidget(sub)
    creator = QLabel("Created by Jainam Maru — Parul University")
    creator.setStyleSheet("font-size: 12px; color: #4A7A9B;")
    creator.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout1.addWidget(creator)
    wizard.addPage(page1)

    # Page 2: Features overview
    page2 = QWizardPage()
    page2.setTitle("What's Included")
    layout2 = QVBoxLayout(page2)
    features = [
        ("📝", "Exam Mode", "Secure, tamper-resistant examination environment"),
        ("📚", "Learn Hub", "Course materials, assignments, and study resources"),
        ("💻", "Dev Suite", "Pre-configured Python, Java, C++, and more"),
        ("🔐", "Cyber Lab", "Isolated cybersecurity practice environments"),
        ("🏫", "Admin Center", "Centralized campus management (admin only)"),
    ]
    for icon, name, desc in features:
        row = QLabel(f"{icon}  <b>{name}</b> — {desc}")
        row.setStyleSheet("font-size: 13px; color: #C8D8E8; margin: 4px 0;")
        row.setTextFormat(Qt.TextFormat.RichText)
        layout2.addWidget(row)
    wizard.addPage(page2)

    # Page 3: Quick start
    page3 = QWizardPage()
    page3.setTitle("You're Ready!")
    layout3 = QVBoxLayout(page3)
    ready_text = QLabel(
        "Your EduOS environment is fully configured.\n\n"
        "• For exams: wait for your instructor to activate Exam Mode\n"
        "• For learning: open Learn Hub from the taskbar\n"
        "• For coding: open Dev Suite to launch your IDE\n\n"
        "Need help? Ask your lab administrator."
    )
    ready_text.setStyleSheet("font-size: 13px; color: #C8D8E8; line-height: 1.6;")
    ready_text.setWordWrap(True)
    layout3.addWidget(ready_text)

    dont_show = QCheckBox("Don't show this again")
    dont_show.setStyleSheet("color: #8BA3C0; font-size: 12px;")
    dont_show.setChecked(True)
    layout3.addWidget(dont_show)
    wizard.addPage(page3)

    wizard.finished.connect(lambda result: (
        WELCOME_FLAG.touch() if dont_show.isChecked() else None
    ))

    wizard.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

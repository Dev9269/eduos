#!/usr/bin/env python3
"""EduOS Welcome - First-run experience for new users"""

import sys, os
from PyQt6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QLabel,
    QPushButton, QCheckBox, QTextEdit
)
from PyQt6.QtGui import QFont, QPixmap, QPalette, QColor
from PyQt6.QtCore import Qt, QSize

WELCOME_FLAG = os.path.expanduser("~/.eduos-welcome-done")

class WelcomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to EduOS")
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        title = QLabel("🎓 EduOS")
        title.setStyleSheet("font-size: 48px; font-weight: bold; color: #2563eb;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Educational Operating System")
        subtitle.setStyleSheet("font-size: 20px; color: #64748b;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        desc = QLabel(
            "EduOS is a Debian-based operating system designed for engineering\n"
            "colleges and universities. It provides a complete campus computing\n"
            "ecosystem for learning, examinations, development, cybersecurity, and administration."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 14px; color: #475569; padding: 20px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)


class ModulesPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("EduOS Modules")
        layout = QVBoxLayout(self)
        modules = [
            ("📚 Learn Hub", "Study materials, assignments, notes, and schedules"),
            ("📝 Exam Mode", "Secure examination environment with timer and encrypted storage"),
            ("⚙ Admin Center", "Centralized campus and lab management"),
            ("🔧 Dev Suite", "Complete engineering programming environment"),
            ("🛡️ Cyber Lab", "Isolated cybersecurity practice laboratories"),
        ]
        for title, desc in modules:
            ml = QLabel(f"<b>{title}</b><br><span style='color: #666;'>{desc}</span>")
            ml.setWordWrap(True)
            ml.setStyleSheet("padding: 12px; background: #f8fafc; border-radius: 8px; margin: 4px;")
            layout.addWidget(ml)


class QuickStartPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Quick Start")
        layout = QVBoxLayout(self)
        tips = QTextEdit()
        tips.setReadOnly(True)
        tips.setStyleSheet("font-size: 13px; border: none; background: transparent;")
        tips.setHtml("""
        <h3>Getting Started with EduOS</h3>
        <ul>
        <li><b>Applications Menu</b> → Bottom left corner (Windows-style)</li>
        <li><b>Learn Hub</b> → Access at <a href="http://localhost:5050">http://localhost:5050</a></li>
        <li><b>Exam Mode</b> → Launch from applications menu or terminal: <code>eduos-exam</code></li>
        <li><b>Admin Center</b> → Launch from applications menu or terminal: <code>eduos-admin</code></li>
        <li><b>Dev Suite</b> → Launch from applications menu or terminal: <code>eduos-devsuite</code></li>
        <li><b>Cyber Lab</b> → Launch from applications menu or terminal: <code>eduos-cyberlab</code></li>
        <li><b>System Info</b> → Terminal: <code>eduos-info</code></li>
        </ul>
        """)
        layout.addWidget(tips)


def main():
    app = QApplication(sys.argv)
    
    if os.path.exists(WELCOME_FLAG):
        print("Welcome already shown")
        return
    
    wizard = QWizard()
    wizard.setWindowTitle("Welcome to EduOS")
    wizard.setMinimumSize(600, 500)
    wizard.setStyleSheet("""
        QWizard { background: white; }
        QWizardPage { background: white; }
    """)
    
    wizard.addPage(WelcomePage())
    wizard.addPage(ModulesPage())
    wizard.addPage(QuickStartPage())
    
    if wizard.exec() == QWizard.DialogCode.Accepted:
        with open(WELCOME_FLAG, "w") as f:
            f.write("done")
        print("Welcome completed")


if __name__ == "__main__":
    main()

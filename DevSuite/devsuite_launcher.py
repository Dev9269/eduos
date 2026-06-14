#!/usr/bin/env python3
"""
EduOS Dev Suite - Development Environment Manager
"""

import sys
import subprocess
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGridLayout, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap


TOOLS = [
    {"name": "VS Code", "icon": "💻", "cmd": "code", "desc": "Visual Studio Code IDE"},
    {"name": "Terminal", "icon": "🖥️", "cmd": "konsole", "desc": "KDE Terminal"},
    {"name": "Python", "icon": "🐍", "cmd": "python3", "desc": "Python 3 Interpreter"},
    {"name": "Java", "icon": "☕", "cmd": "bash -c 'java -version; read'", "desc": "Java Runtime"},
    {"name": "Node.js", "icon": "🟢", "cmd": "bash -c 'node --version; read'", "desc": "Node.js Runtime"},
    {"name": "Git GUI", "icon": "🔀", "cmd": "gitk", "desc": "Git Repository Browser"},
    {"name": "Docker", "icon": "🐳", "cmd": "konsole -e 'docker ps'", "desc": "Docker Container Manager"},
    {"name": "Database", "icon": "🗄️", "cmd": "sqlitebrowser", "desc": "SQLite Database Browser"},
    {"name": "GCC/G++", "icon": "⚙️", "cmd": "bash -c 'gcc --version; g++ --version; read'", "desc": "C/C++ Compilers"},
    {"name": ".NET", "icon": "🔷", "cmd": "bash -c 'dotnet --version 2>/dev/null || echo .NET not in PATH; read'", "desc": ".NET SDK"},
    {"name": "CMake", "icon": "📐", "cmd": "bash -c 'cmake --version; read'", "desc": "CMake Build System"},
    {"name": "Kate Editor", "icon": "📝", "cmd": "kate", "desc": "Advanced Text Editor"},
]


class DevSuiteWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduOS Dev Suite - Development Environment")
        self.setMinimumSize(800, 600)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        header = QWidget()
        header.setStyleSheet("background: #0f172a; border-radius: 12px; padding: 16px;")
        hlayout = QHBoxLayout(header)
        title = QLabel("🔧 EduOS Dev Suite")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        hlayout.addWidget(title)
        hlayout.addStretch()
        info = QLabel("Engineering Programming Environment")
        info.setStyleSheet("font-size: 13px; color: #94a3b8;")
        hlayout.addWidget(info)
        layout.addWidget(header)

        welcome = QLabel(
            "Welcome to the EduOS Development Suite.\n"
            "All engineering programming tools are preinstalled and ready to use."
        )
        welcome.setStyleSheet("font-size: 14px; color: #475569; padding: 12px; background: #f8fafc; border-radius: 8px; margin: 8px 0;")
        layout.addWidget(welcome)

        grid = QGridLayout()
        grid.setSpacing(12)

        row, col = 0, 0
        for tool in TOOLS:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background: white; border: 1px solid #e8edf5;
                    border-radius: 12px; padding: 16px;
                }
                QFrame:hover {
                    background: #f8fafc; border-color: #2563eb;
                    transform: translateY(-2px);
                }
            """)
            card.setFixedSize(200, 140)
            card_layout = QVBoxLayout(card)

            icon = QLabel(tool["icon"])
            icon.setStyleSheet("font-size: 32px;")
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(icon)

            name = QLabel(tool["name"])
            name.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e293b;")
            name.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(name)

            desc = QLabel(tool["desc"])
            desc.setStyleSheet("font-size: 11px; color: #94a3b8;")
            desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc.setWordWrap(True)
            card_layout.addWidget(desc)

            card.mousePressEvent = lambda e, c=tool["cmd"]: self._launch_tool(c)

            grid.addWidget(card, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

        layout.addLayout(grid)
        layout.addStretch()

    def _launch_tool(self, cmd):
        try:
            subprocess.Popen(["bash", "-c", cmd], start_new_session=True)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to launch tool: {e}")


def main():
    app = QApplication(sys.argv)
    window = DevSuiteWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

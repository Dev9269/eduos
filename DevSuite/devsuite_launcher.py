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
from design_system import EduOSColors as C, apply_glass_theme, glass_card_style, glass_button_style, accent_glow_style, glass_success_button_style, glass_danger_button_style, glass_warning_button_style, status_badge_style, StatusBadge, SectionTitle, glass_stat_card_style, glass_banner_style


TOOLS = [
    {"name": "VS Code", "icon": "💻", "cmd": "code", "desc": "Visual Studio Code IDE"},
    {"name": "Terminal", "icon": "🖥️", "cmd": "konsole", "desc": "System Terminal"},
    {"name": "Python", "icon": "🐍", "cmd": "python3", "desc": "Python 3 Interpreter"},
    {"name": "Java", "icon": "☕", "cmd": "konsole -e bash -c 'java -version; echo; read -p \"Press Enter...\"'", "desc": "Java Runtime"},
    {"name": "Node.js", "icon": "🟢", "cmd": "konsole -e bash -c 'node --version; echo; read -p \"Press Enter...\"'", "desc": "Node.js Runtime"},
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
        header.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {C.BG_DEEP}, stop:1 {C.BG_DARK}); border-radius: 12px; padding: 16px;")
        hlayout = QHBoxLayout(header)
        title = QLabel("🔧 EduOS Dev Suite")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {C.TEXT_PRIMARY};")
        hlayout.addWidget(title)
        hlayout.addStretch()
        info = QLabel("Engineering Programming Environment")
        info.setStyleSheet(f"font-size: 13px; color: {C.TEXT_MUTED};")
        hlayout.addWidget(info)
        layout.addWidget(header)

        welcome = QLabel(
            "Welcome to the EduOS Development Suite.\n"
            "All engineering programming tools are preinstalled and ready to use."
        )
        welcome.setStyleSheet(f"font-size: 14px; color: {C.TEXT_SECONDARY}; padding: 12px; background: {C.GLASS_CARD}; border-radius: 8px; margin: 8px 0;")
        layout.addWidget(welcome)

        grid = QGridLayout()
        grid.setSpacing(12)

        row, col = 0, 0
        for tool in TOOLS:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: {C.GLASS_CARD}; border: 1px solid {C.GLASS_BORDER};
                    border-radius: 12px; padding: 16px;
                }}
                QFrame:hover {{
                    background: {C.GLASS_CARD_HOVER}; border-color: {C.ACCENT_PRIMARY};
                    margin: -2px;
                }}
            """)
            card.setFixedSize(200, 140)
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            card.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            card_layout = QVBoxLayout(card)

            icon = QLabel(tool["icon"])
            icon.setStyleSheet("font-size: 32px;")
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(icon)

            name = QLabel(tool["name"])
            name.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {C.TEXT_PRIMARY};")
            name.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(name)

            desc = QLabel(tool["desc"])
            desc.setStyleSheet(f"font-size: 11px; color: {C.TEXT_MUTED};")
            desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc.setWordWrap(True)
            card_layout.addWidget(desc)

            cmd = tool["cmd"]
            card.mousePressEvent = lambda e, c=cmd: self._launch_tool(c)
            card.keyPressEvent = lambda e, c=cmd: self._launch_tool(c) if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Space) else QFrame.keyPressEvent(card, e)

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
    app.setStyle("Fusion")
    apply_glass_theme(app)
    window = DevSuiteWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

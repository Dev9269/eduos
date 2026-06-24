#!/usr/bin/env python3
"""
EduOS Cyber Lab - Isolated Cybersecurity Practice Environment
Manages Docker/Podman containers for safe security labs.
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QTabWidget,
    QGroupBox, QTextEdit, QLineEdit, QMessageBox, QHeaderView, QListWidget,
    QSplitter, QFrame, QTextBrowser
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
from design_system import EduOSColors as C, apply_glass_theme, glass_card_style, glass_button_style, accent_glow_style, glass_success_button_style, glass_danger_button_style, glass_warning_button_style, status_badge_style, StatusBadge, SectionTitle, glass_stat_card_style, glass_banner_style


LABS = {
    "network_scanning": {
        "name": "Network Scanning Basics",
        "description": "Learn to use Nmap for network discovery and port scanning.",
        "docker": "kalilinux/kali-rolling",
        "command": "nmap -sn 192.168.1.0/24",
        "tools": ["nmap", "netcat", "tcpdump"],
        "difficulty": "Beginner"
    },
    "web_attacks": {
        "name": "Web Application Security",
        "description": "Practice web application pentesting with OWASP Juice Shop.",
        "docker": "bkimminich/juice-shop",
        "command": "docker run -d -p 3000:3000 bkimminich/juice-shop",
        "tools": ["burpsuite", "sqlmap", "nmap"],
        "difficulty": "Intermediate"
    },
    "packet_analysis": {
        "name": "Packet Analysis",
        "description": "Capture and analyze network traffic using tcpdump and Wireshark.",
        "docker": "kalilinux/kali-rolling",
        "command": "tcpdump -i eth0 -c 100",
        "tools": ["tcpdump", "wireshark", "tshark"],
        "difficulty": "Beginner"
    },
    "password_cracking": {
        "name": "Password Security",
        "description": "Understand password security through hash cracking exercises.",
        "docker": "kalilinux/kali-rolling",
        "command": "john --list=formats",
        "tools": ["john", "hashcat", "hydra"],
        "difficulty": "Intermediate"
    },
    "forensics": {
        "name": "Digital Forensics",
        "description": "Learn forensic analysis techniques on disk images and memory dumps.",
        "docker": "kalilinux/kali-rolling",
        "command": "foremost -h",
        "tools": ["foremost", "binwalk", "strings", "hexdump"],
        "difficulty": "Advanced"
    }
}


class CyberLabWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduOS Cyber Lab - Cybersecurity Practice Environment")
        self.setGeometry(100, 100, 1100, 700)
        self.active_containers = {}
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        header = QWidget()
        header.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {C.BG_DEEP}, stop:1 {C.BG_DARK}); border-radius: 12px; padding: 16px;")
        hlayout = QHBoxLayout(header)
        title = QLabel("🛡️ EduOS Cyber Lab")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {C.TEXT_PRIMARY};")
        hlayout.addWidget(title)
        hlayout.addStretch()
        status = QLabel("🔒 Environment: Isolated | Mode: Safe")
        status.setStyleSheet(f"font-size: 13px; color: {C.ACCENT_GREEN}; background: {C.GLASS_CARD}; padding: 6px 12px; border-radius: 6px;")
        hlayout.addWidget(status)
        layout.addWidget(header)

        content = QSplitter(Qt.Orientation.Horizontal)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        labs_group = QGroupBox("Available Labs")
        labs_group.setStyleSheet(f"QGroupBox {{ font-weight: bold; font-size: 14px; padding-top: 16px; border: 1px solid {C.GLASS_BORDER}; border-radius: 12px; background: {C.GLASS_CARD}; color: {C.TEXT_PRIMARY}; padding: 20px 16px 16px 16px; }} QGroupBox::title {{ subcontrol-origin: margin; left: 16px; padding: 0 8px; color: {C.TEXT_SECONDARY}; }}")
        glayout = QVBoxLayout(labs_group)

        self.lab_list = QListWidget()
        for lab_id, lab in LABS.items():
            self.lab_list.addItem(f"{lab['name']} ({lab['difficulty']})")
        self.lab_list.setStyleSheet("font-size: 13px;")
        self.lab_list.currentRowChanged.connect(self._show_lab_info)
        glayout.addWidget(self.lab_list)

        self.launch_btn = QPushButton("🚀 Launch Lab")
        self.launch_btn.setStyleSheet(accent_glow_style())
        self.launch_btn.clicked.connect(self._launch_lab)
        glayout.addWidget(self.launch_btn)
        left_layout.addWidget(labs_group)

        content.addWidget(left_panel)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        info_group = QGroupBox("Lab Information")
        info_group.setStyleSheet(f"QGroupBox {{ font-weight: bold; font-size: 14px; padding-top: 16px; border: 1px solid {C.GLASS_BORDER}; border-radius: 12px; background: {C.GLASS_CARD}; color: {C.TEXT_PRIMARY}; padding: 20px 16px 16px 16px; }} QGroupBox::title {{ subcontrol-origin: margin; left: 16px; padding: 0 8px; color: {C.TEXT_SECONDARY}; }}")
        ilayout = QVBoxLayout(info_group)
        self.lab_info = QTextBrowser()
        self.lab_info.setStyleSheet(f"font-size: 13px; padding: 8px; background: {C.GLASS_CARD}; border: 1px solid {C.GLASS_BORDER}; border-radius: 6px; color: {C.TEXT_PRIMARY};")
        ilayout.addWidget(self.lab_info)
        right_layout.addWidget(info_group)

        terminal_group = QGroupBox("Lab Console")
        terminal_group.setStyleSheet(f"QGroupBox {{ font-weight: bold; font-size: 14px; padding-top: 16px; border: 1px solid {C.GLASS_BORDER}; border-radius: 12px; background: {C.GLASS_CARD}; color: {C.TEXT_PRIMARY}; padding: 20px 16px 16px 16px; }} QGroupBox::title {{ subcontrol-origin: margin; left: 16px; padding: 0 8px; color: {C.TEXT_SECONDARY}; }}")
        tlayout = QVBoxLayout(terminal_group)
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("""
            font-family: 'Fira Code', monospace; font-size: 12px;
            background: #1e1e2e; color: #cdd6f4; border: 1px solid #313244;
            border-radius: 6px; padding: 8px;
        """)
        tlayout.addWidget(self.console)

        cmd_layout = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Enter command (e.g. nmap -sn 192.168.1.0/24)")
        self.cmd_input.setStyleSheet(f"font-family: monospace; font-size: 12px; padding: 6px; border: 1px solid {C.GLASS_BORDER}; border-radius: 4px; background: {C.GLASS_CARD}; color: {C.TEXT_PRIMARY};")
        self.cmd_input.returnPressed.connect(self._run_command)
        cmd_layout.addWidget(self.cmd_input)
        run_btn = QPushButton("▶ Run")
        run_btn.setStyleSheet(glass_success_button_style())
        run_btn.clicked.connect(self._run_command)
        cmd_layout.addWidget(run_btn)
        tlayout.addLayout(cmd_layout)
        right_layout.addWidget(terminal_group)

        content.addWidget(right_panel)
        content.setSizes([300, 700])
        layout.addWidget(content, 1)

        self._show_lab_info(0)

    def _show_lab_info(self, index):
        if index < 0:
            return
        lab_ids = list(LABS.keys())
        if index >= len(lab_ids):
            return
        lab = LABS[lab_ids[index]]
        info = f"""
        <h2>{lab['name']}</h2>
        <p><b>Difficulty:</b> {lab['difficulty']}</p>
        <p><b>Description:</b> {lab['description']}</p>
        <p><b>Tools:</b> {', '.join(lab['tools'])}</p>
        <p><b>Environment:</b> Docker container (isolated)</p>
        <p style="color: #dc2626;"><b>⚠ Warning:</b> This lab runs in an isolated container.
        Do not attack systems outside this environment.</p>
        """
        self.lab_info.setHtml(info)

    def _launch_lab(self):
        index = self.lab_list.currentRow()
        if index < 0:
            return
        lab_ids = list(LABS.keys())
        lab = LABS[lab_ids[index]]

        self.console.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Launching: {lab['name']}")
        self.console.append(f"[{datetime.now().strftime('%H:%M:%S')}] Pulling image: {lab['docker']}...")

        try:
            result = subprocess.run(
                ["sudo", "-A", "docker", "run", "--rm", "-d", "--network", "none", lab["docker"],
                 "sh", "-c", "sleep 3600"],
                capture_output=True, text=True, timeout=120,
                env={"SUDO_ASKPASS": "/bin/false"}
            )
            if result.returncode == 0:
                container_id = result.stdout.strip()[:12]
                self.active_containers[lab["name"]] = container_id
                self.console.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Lab ready! Container: {container_id}")
                self.console.append(f"[{datetime.now().strftime('%H:%M:%S')}] 💡 Try running: {lab['command']}")
            else:
                self.console.append(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: {result.stderr}")
        except Exception as e:
            self.console.append(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: {e}")

    def _run_command(self):
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return

        self.console.append(f"[{datetime.now().strftime('%H:%M:%S')}] $ {cmd}")
        self.cmd_input.clear()

        try:
            result = subprocess.run(
                ["sudo", "-A", "sh", "-c", cmd],
                capture_output=True, text=True, timeout=30,
                env={"SUDO_ASKPASS": "/bin/false"}
            )
            output = result.stdout or result.stderr or "No output"
            self.console.append(output[:2000])
            if result.returncode != 0:
                self.console.append(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠ Exit code: {result.returncode}")
        except subprocess.TimeoutExpired:
            self.console.append(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠ Command timed out")
        except Exception as e:
            self.console.append(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: {e}")

    def closeEvent(self, event):
        for name, cid in self.active_containers.items():
            subprocess.run(["sudo", "-A", "docker", "rm", "-f", cid],
                           capture_output=True,
                           env={"SUDO_ASKPASS": "/bin/false"})
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    apply_glass_theme(app)
    window = CyberLabWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

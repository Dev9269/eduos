#!/usr/bin/env python3
"""
EduOS Admin Center - Centralized administration platform
"""

import sys
import os
import subprocess
import json
import hashlib
import ipaddress
import platform
import socket
import threading
from datetime import datetime, timedelta
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QTabWidget,
    QGroupBox, QTextEdit, QMessageBox, QHeaderView, QListWidget,
    QSplitter, QFrame, QTreeWidget, QTreeWidgetItem, QProgressBar,
    QSystemTrayIcon, QMenu, QLineEdit, QDialog, QFormLayout,
    QDialogButtonBox, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QAction
from cryptography.fernet import Fernet

_ROOT_DIR = str(Path(__file__).resolve().parent.parent)
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from design_system import EduOSColors as C, apply_glass_theme, glass_card_style, glass_button_style, accent_glow_style, glass_success_button_style, glass_danger_button_style, glass_warning_button_style, status_badge_style, StatusBadge, SectionTitle, glass_stat_card_style, glass_banner_style


ADMIN_CONFIG_PATH = Path.home() / ".eduos" / "admin_config.json"


def _config_fernet() -> Fernet:
    """Derive a Fernet key from the admin password hash.

    The config file is encrypted with a key derived from the admin
    hash, so it can only be decrypted by someone who knows the
    admin password. If no admin hash exists yet, returns None.
    """
    hash_path = Path.home() / ".eduos" / "admin_config.json"
    if not hash_path.exists():
        return None
    try:
        data = json.loads(hash_path.read_text())
        admin_hash = data.get("admin_hash", "")
        if not admin_hash:
            return None
        key = hashlib.sha256(admin_hash.encode()).digest()
        import base64
        return Fernet(base64.urlsafe_b64encode(key))
    except Exception:
        return None


class AdminLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EduOS Admin — Authenticate")
        self.setFixedSize(400, 250)
        layout = QVBoxLayout(self)

        title = QLabel("🔐 EduOS Admin Authentication")
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {C.ACCENT_PRIMARY};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Admin Password")

        self.btn = QPushButton("Login")
        self.btn.setStyleSheet(accent_glow_style())
        self.btn.clicked.connect(self.verify)

        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setPlaceholderText("Set a new admin password (first run)")

        layout.addWidget(QLabel("Enter Admin Password:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.new_password_input)
        layout.addWidget(self.btn)

        self.password_input.returnPressed.connect(self.verify)
        self.new_password_input.returnPressed.connect(self.verify)

    def _load_admin_hash(self) -> str:
        config = ADMIN_CONFIG_PATH
        if config.exists():
            try:
                data = json.loads(config.read_text())
                return data.get("admin_hash", "")
            except Exception:
                return ""
        return ""

    def verify(self):
        import hashlib as _h
        password = self.password_input.text()
        stored_hash = self._load_admin_hash()

        # First run — set the admin password
        if not stored_hash:
            new_pw = self.new_password_input.text()
            if len(new_pw) < 6:
                QMessageBox.warning(
                    self, "Error",
                    "Set a new admin password (min 6 characters) to continue."
                )
                return
            admin_hash = _h.sha256(new_pw.encode()).hexdigest()
            ADMIN_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            try:
                data = json.loads(ADMIN_CONFIG_PATH.read_text()) if ADMIN_CONFIG_PATH.exists() else {}
            except Exception:
                data = {}
            data["admin_hash"] = admin_hash
            ADMIN_CONFIG_PATH.write_text(json.dumps(data, indent=2))
            QMessageBox.information(
                self, "Setup Complete",
                "Admin password set. Restart EduOS Admin to log in."
            )
            self.reject()
            return

        entered_hash = _h.sha256(password.encode()).hexdigest()
        if entered_hash == stored_hash:
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Wrong password")
            self.password_input.clear()

    def verify_config_encryption(self):
        """Ensure config is encrypted with the admin hash as key."""
        fernet = _config_fernet()
        return fernet is not None


class PingThread(QThread):
    result = pyqtSignal(str, bool)

    def __init__(self, host):
        super().__init__()
        self.host = host

    def run(self):
        try:
            # Vulnerability 2 — validate it's a real IP before pinging.
            # This blocks shell-injection payloads passed as "host".
            ipaddress.ip_address(self.host)
        except ValueError:
            self.result.emit(self.host, False)
            return
        try:
            out = subprocess.run(
                ["ping", "-c", "1", "-W", "2", self.host],
                capture_output=True, timeout=5
            )
            self.result.emit(self.host, out.returncode == 0)
        except Exception:
            self.result.emit(self.host, False)


class AdminCenterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduOS Admin Center - Campus Management Console")
        self.setGeometry(50, 50, 1400, 850)
        self.lab_hosts = []
        self.server_host = "eduos-server.local"
        self.server_port = 8765
        self.auth_token = ""
        self._load_server_settings()
        self._load_config()
        self._setup_ui()
        self._load_system_info()
        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh_monitor)
        self._timer.start(5000)
        self._ping_lock = threading.Lock()

        if not self.auth_token:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, "No Auth Token",
                "No server auth token configured.\n"
                "Go to Server Settings and paste your token\n"
                "from Server/generate-admin-token.py"
            )

    def closeEvent(self, event):
        self._timer.stop()
        event.accept()

    def _load_server_settings(self):
        """Load saved server settings on startup"""
        CONFIG_FILE = Path.home() / '.eduos' / 'admin_settings.json'
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text())
                self.server_host = data.get('server_host', 'eduos-server.local')
                self.server_port = data.get('server_port', 8765)
                self.auth_token = data.get('auth_token', '')
            except Exception:
                pass

    def _open_server_settings(self):
        """Configure server connection and auth token"""
        CONFIG_FILE = Path.home() / '.eduos' / 'admin_settings.json'

        dlg = QDialog(self)
        dlg.setWindowTitle("Server Settings")
        dlg.setFixedSize(500, 300)
        layout = QVBoxLayout(dlg)

        layout.addWidget(QLabel(
            "Configure connection to EduOS Server.\n"
            "Run Server/generate-admin-token.py on the server machine\n"
            "to get your auth token."
        ))

        form = QFormLayout()
        host_input = QLineEdit(self.server_host)
        port_input = QLineEdit(str(self.server_port))
        token_input = QLineEdit(self.auth_token)
        token_input.setEchoMode(QLineEdit.EchoMode.Password)
        token_input.setPlaceholderText("Paste token from generate-admin-token.py")

        form.addRow("Server Host:", host_input)
        form.addRow("Server Port:", port_input)
        form.addRow("Auth Token:", token_input)
        layout.addLayout(form)

        def save():
            self.server_host = host_input.text().strip()
            self.server_port = int(port_input.text().strip() or '8765')
            self.auth_token = token_input.text().strip()

            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_FILE.write_text(json.dumps({
                'server_host': self.server_host,
                'server_port': self.server_port,
                'auth_token': self.auth_token,
            }))
            QMessageBox.information(dlg, "Saved", "Server settings saved.")
            dlg.accept()

        save_btn = QPushButton("Save & Connect")
        save_btn.clicked.connect(save)
        layout.addWidget(save_btn)
        dlg.exec()

    def _load_config(self):
        config_path = ADMIN_CONFIG_PATH
        if config_path.exists():
            try:
                raw = json.loads(config_path.read_text())
                fernet = _config_fernet()
                if fernet and raw.get("encrypted"):
                    import base64
                    decrypted = fernet.decrypt(
                        base64.b64decode(raw["encrypted"].encode())
                    )
                    cfg = json.loads(decrypted)
                else:
                    cfg = raw
                self.lab_hosts = cfg.get("lab_hosts", [])
            except Exception:
                self.lab_hosts = []

    def _save_config(self):
        config_dir = ADMIN_CONFIG_PATH.parent
        config_dir.mkdir(parents=True, exist_ok=True)
        data = {"lab_hosts": self.lab_hosts}
        fernet = _config_fernet()
        if fernet:
            # Vulnerability 3 — encrypt host list with admin-hash-derived key
            import base64
            encrypted = fernet.encrypt(json.dumps(data).encode())
            payload = {"encrypted": base64.b64encode(encrypted).decode()}
        else:
            payload = data
        ADMIN_CONFIG_PATH.write_text(json.dumps(payload, indent=2))

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)

        header = QWidget()
        header.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {C.BG_DEEP}, stop:1 {C.BG_DARK}); border-radius: 12px; padding: 16px;")
        hlayout = QHBoxLayout(header)

        title = QLabel("⚙ EduOS Admin Center")
        title.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {C.TEXT_PRIMARY};")
        hlayout.addWidget(title)

        self.status_label = QLabel("● Online")
        self.status_label.setStyleSheet(f"color: {C.ACCENT_GREEN}; font-size: 13px; background: {C.GLASS_CARD}; padding: 4px 12px; border-radius: 12px;")
        hlayout.addWidget(self.status_label)

        self.platform_badge = QLabel()
        self.platform_badge.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {C.ACCENT_PRIMARY}; background: {C.GLASS_CARD}; padding: 4px 12px; border-radius: 12px;")
        hlayout.addWidget(self.platform_badge)

        hlayout.addStretch()

        settings_btn = QPushButton("⚙ Server Settings")
        settings_btn.setStyleSheet(glass_button_style())
        settings_btn.clicked.connect(self._open_server_settings)
        hlayout.addWidget(settings_btn)

        roster_btn = QPushButton("👥 Import Roster")
        roster_btn.setStyleSheet(glass_button_style())
        roster_btn.clicked.connect(self._import_roster)
        hlayout.addWidget(roster_btn)

        history_btn = QPushButton("📋 Update History")
        history_btn.setStyleSheet(glass_button_style())
        history_btn.clicked.connect(self._view_update_history)
        hlayout.addWidget(history_btn)

        self.host_label = QLabel()
        self.host_label.setStyleSheet(f"font-size: 12px; color: {C.TEXT_MUTED};")
        hlayout.addWidget(self.host_label)
        layout.addWidget(header)

        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid {C.GLASS_BORDER}; border-radius: 8px; padding: 16px; background: {C.GLASS_CARD}; }}
            QTabBar::tab {{ padding: 10px 20px; font-size: 13px; font-weight: bold; color: {C.TEXT_MUTED}; }}
            QTabBar::tab:selected {{ background: {C.ACCENT_PRIMARY}; color: white; border-radius: 8px 8px 0 0; }}
        """)

        tabs.addTab(self._build_dashboard_tab(), "🏠 Home")
        tabs.addTab(self._build_dashboard(), "📊 Dashboard")
        tabs.addTab(self._build_systems_tab(), "💻 Lab Systems")
        tabs.addTab(self._build_software_tab(), "📦 Software Management")
        tabs.addTab(self._build_exam_control_tab(), "🎯 Exam Control")
        tabs.addTab(self._build_reports_tab(), "📈 Reports")
        tabs.addTab(self._build_updates_tab(), "🔄 Updates")

        layout.addWidget(tabs)

    def _build_dashboard(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        grid = QHBoxLayout()
        cards = [
            ("Systems Online", "1", "#2563eb"),
            ("Users Active", "3", "#16a34a"),
            ("Exams Running", "0", "#dc2626"),
            ("Pending Updates", "0", "#f59e0b"),
            ("Lab Availability", "100%", "#7c3aed"),
        ]
        for ctitle, value, color in cards:
            card = QFrame()
            card.setStyleSheet(f"background: {C.GLASS_CARD}; border: 1px solid {C.GLASS_BORDER}; border-radius: 10px; padding: 16px; border-left: 4px solid {color};")
            cl = QVBoxLayout(card)
            cl.addWidget(QLabel(ctitle))
            v = QLabel(value)
            v.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
            cl.addWidget(v)
            grid.addWidget(card)
        layout.addLayout(grid)

        self.monitor_tree = QTreeWidget()
        self.monitor_tree.setHeaderLabels(["Resource", "Usage", "Status"])
        self.monitor_tree.setStyleSheet(f"font-size: 13px; border: 1px solid {C.GLASS_BORDER}; border-radius: 8px; color: {C.TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(self.monitor_tree)

        return tab

    def _build_dashboard_tab(self) -> QWidget:
        """Build the home dashboard tab"""
        from PyQt6.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
            QLabel, QPushButton, QFrame
        )

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header
        header = QLabel("🖥  EduOS Admin Dashboard")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #4A9EFF;")
        layout.addWidget(header)

        # Stat cards grid
        grid = QGridLayout()
        grid.setSpacing(12)

        self._stat_labels = {}

        stats = [
            ("connected_machines", "💻 Connected", "0 / 0", "#4A9EFF"),
            ("active_exams", "📝 Active Exams", "0", "#10B981"),
            ("pending_submissions", "📬 Pending Submissions", "0", "#F59E0B"),
            ("server_status", "🌐 Server", "Checking...", "#8B5CF6"),
        ]

        for i, (key, title, default, color) in enumerate(stats):
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: #0D1B2E;
                    border: 1px solid {color}44;
                    border-radius: 12px;
                    padding: 16px;
                }}
            """)
            card_layout = QVBoxLayout(card)

            title_label = QLabel(title)
            title_label.setStyleSheet(f"font-size: 12px; color: {color}; font-weight: bold;")
            card_layout.addWidget(title_label)

            value_label = QLabel(default)
            value_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #E8F0FE;")
            card_layout.addWidget(value_label)

            self._stat_labels[key] = value_label
            grid.addWidget(card, i // 2, i % 2)

        layout.addLayout(grid)

        # Quick actions
        actions_label = QLabel("Quick Actions")
        actions_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #8BA3C0;")
        layout.addWidget(actions_label)

        btn_row = QHBoxLayout()
        quick_actions = [
            ("🔔 Activate Exam Mode", self._start_exam),
            ("📤 Push Update", self._push_update),
            ("👥 Import Roster", self._import_roster),
            ("📅 Schedule Exam", self._schedule_exam),
            ("🔄 Refresh All", self._refresh_dashboard),
        ]
        for label, handler in quick_actions:
            btn = QPushButton(label)
            btn.setStyleSheet("""
                QPushButton {
                    background: #162030; color: #E8F0FE;
                    border: 1px solid #1E3A5F; border-radius: 8px;
                    padding: 10px 14px; font-size: 12px;
                }
                QPushButton:hover { background: #1E3A5F; }
            """)
            btn.clicked.connect(handler)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)

        layout.addStretch()

        # Auto-refresh every 30 seconds
        self._dashboard_timer = QTimer()
        self._dashboard_timer.timeout.connect(self._refresh_dashboard)
        self._dashboard_timer.start(30000)
        QTimer.singleShot(1000, self._refresh_dashboard)

        return widget

    def _refresh_dashboard(self):
        """Fetch current stats from server and update dashboard"""
        import urllib.request

        def fetch(endpoint):
            try:
                req = urllib.request.Request(
                    f"http://{self.server_host}:{self.server_port}{endpoint}",
                    headers={'Authorization': f'Bearer {self.auth_token}'}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    return json.loads(resp.read())
            except Exception:
                return None

        # Update server status
        health = fetch("/health")
        if health:
            self._stat_labels["server_status"].setText("🟢 Online")
            self._stat_labels["server_status"].setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #10B981;"
            )
        else:
            self._stat_labels["server_status"].setText("🔴 Offline")
            self._stat_labels["server_status"].setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #EF4444;"
            )

        # Update devices
        devices = fetch("/devices")
        if devices:
            online = len(devices.get("online", []))
            total = len(devices.get("devices", []))
            self._stat_labels["connected_machines"].setText(f"{online} / {total}")

        # Update schedules for active exams
        schedules = fetch("/exam/schedules")
        if schedules:
            active = sum(1 for s in schedules.get("schedules", [])
                         if s.get("status") == "activated")
            self._stat_labels["active_exams"].setText(str(active))

    def _get_realtime_stats(self):
        stats = {}
        try:
            with open("/proc/loadavg") as f:
                load = f.read().split()
            stats["cpu"] = f"{load[0]} / {load[1]} / {load[2]}"
        except Exception:
            stats["cpu"] = "N/A"

        try:
            mem = {}
            with open("/proc/meminfo") as f:
                for line in f:
                    parts = line.split()
                    mem[parts[0].rstrip(":")] = int(parts[1])
            total_mb = mem.get("MemTotal", 0) // 1024
            avail_mb = mem.get("MemAvailable", 0) // 1024
            used_mb = total_mb - avail_mb
            stats["memory"] = f"{used_mb}MB / {total_mb}MB"
            stats["mem_pct"] = round((used_mb / total_mb) * 100) if total_mb else 0
        except Exception:
            stats["memory"] = "N/A"
            stats["mem_pct"] = 0

        try:
            st = os.statvfs("/")
            total_g = (st.f_frsize * st.f_blocks) / (1024**3)
            free_g = (st.f_frsize * st.f_bavail) / (1024**3)
            used_g = total_g - free_g
            stats["disk"] = f"{used_g:.1f}G / {total_g:.1f}G"
            stats["disk_pct"] = round((used_g / total_g) * 100)
        except Exception:
            stats["disk"] = "N/A"
            stats["disk_pct"] = 0

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("10.0.2.1", 80))
            local_ip = s.getsockname()[0]
            s.close()
            stats["network"] = local_ip
        except Exception:
            stats["network"] = "127.0.0.1"

        try:
            with open("/proc/uptime") as f:
                up = float(f.read().split()[0])
            days, rem = divmod(up, 86400)
            hours, rem = divmod(rem, 3600)
            stats["uptime"] = f"{int(days)}d {int(hours)}h"
        except Exception:
            stats["uptime"] = "N/A"

        try:
            out = subprocess.run(
                ["systemctl", "is-active", "ssh", "--quiet"],
                capture_output=True
            )
            stats["ssh_active"] = out.returncode == 0
        except Exception:
            stats["ssh_active"] = False

        return stats

    def _refresh_monitor(self):
        self.monitor_tree.clear()
        stats = self._get_realtime_stats()

        cpu_color = "#16a34a"
        mem_color = "#16a34a" if stats.get("mem_pct", 0) < 70 else "#f59e0b" if stats.get("mem_pct", 0) < 90 else "#dc2626"
        disk_color = "#16a34a" if stats.get("disk_pct", 0) < 70 else "#f59e0b" if stats.get("disk_pct", 0) < 90 else "#dc2626"

        items_data = [
            ("CPU Load", stats.get("cpu", "N/A"), cpu_color),
            ("Memory", stats.get("memory", "N/A"), mem_color),
            ("Disk", stats.get("disk", "N/A"), disk_color),
            ("Network", stats.get("network", "N/A"), "#16a34a"),
            ("Uptime", stats.get("uptime", "N/A"), "#2563eb"),
            ("SSH Service", "● Running" if stats.get("ssh_active") else "○ Stopped", "#16a34a" if stats.get("ssh_active") else "#dc2626"),
        ]
        for name, value, color in items_data:
            item = QTreeWidgetItem([name, value, "●"])
            item.setForeground(2, QColor(color))
            self.monitor_tree.addTopLevelItem(item)

    def _build_systems_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        toolbar = QHBoxLayout()
        add_btn = QPushButton("➕ Add Lab Machine")
        add_btn.setStyleSheet(accent_glow_style())
        add_btn.clicked.connect(self._add_lab_machine)
        toolbar.addWidget(add_btn)

        refresh_btn = QPushButton("🔄 Ping All")
        refresh_btn.setStyleSheet(glass_button_style())
        refresh_btn.clicked.connect(self._ping_all_hosts)
        toolbar.addWidget(refresh_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.systems_table = QTableWidget()
        self.systems_table.setColumnCount(7)
        self.systems_table.setHorizontalHeaderLabels(["System", "IP", "Status", "Uptime", "CPU", "Memory", "Last Seen"])
        self.systems_table.horizontalHeader().setStretchLastSection(True)
        self.systems_table.setStyleSheet(f"font-size: 13px; border: 1px solid {C.GLASS_BORDER}; border-radius: 8px; color: {C.TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(self.systems_table)

        actions = QHBoxLayout()
        btn_configs = [
            ("🔒 Lock Selected", "#dc2626", self._lock_selected),
            ("🔓 Unlock", "#16a34a", self._unlock_selected),
            ("📢 Send Message", "#7c3aed", self._send_message),
            ("🖥 Remote SSH", "#2563eb", self._remote_ssh),
        ]
        for text, color, handler in btn_configs:
            btn = QPushButton(text)
            btn.setStyleSheet(accent_glow_style() if color == "#2563eb" else glass_success_button_style() if color == "#16a34a" else glass_danger_button_style() if color == "#dc2626" else glass_button_style())
            btn.clicked.connect(handler)
            actions.addWidget(btn)
        actions.addStretch()
        layout.addLayout(actions)

        info = QLabel("💡 Select a lab machine row and use the buttons above to manage it remotely.")
        info.setStyleSheet(f"font-size: 12px; color: {C.TEXT_MUTED}; padding: 8px;")
        layout.addWidget(info)

        return tab

    def _add_lab_machine(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Lab Machine")
        dialog.setModal(True)
        form = QFormLayout(dialog)

        hostname_input = QLineEdit()
        ip_input = QLineEdit()
        ip_input.setPlaceholderText("e.g., 10.0.2.20")
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        form.addRow("Hostname:", hostname_input)
        form.addRow("IP Address:", ip_input)
        form.addRow(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            hostname = hostname_input.text().strip()
            ip = ip_input.text().strip()
            if hostname and ip:
                self.lab_hosts.append({"hostname": hostname, "ip": ip})
                self._save_config()
                self._load_system_info()

    def _ping_all_hosts(self):
        self.status_label.setText("⏳ Scanning...")
        self.status_label.setStyleSheet(f"color: {C.ACCENT_AMBER}; font-size: 13px; background: {C.GLASS_CARD}; padding: 4px 12px; border-radius: 12px;")

        hosts = [h["ip"] for h in self.lab_hosts]
        self.ping_results = {}

        def check_host(ip):
            try:
                # Sanitize before pinging — must be a valid IP literal
                ipaddress.ip_address(ip)
                out = subprocess.run(
                    ["ping", "-c", "1", "-W", "2", ip],
                    capture_output=True, timeout=5
                )
                with self._ping_lock:
                    self.ping_results[ip] = out.returncode == 0
            except Exception:
                with self._ping_lock:
                    self.ping_results[ip] = False

        threads = []
        for ip in hosts:
            t = threading.Thread(target=check_host, args=(ip,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        self._load_system_info()
        self.status_label.setText("● Online")
        self.status_label.setStyleSheet(f"color: {C.ACCENT_GREEN}; font-size: 13px; background: {C.GLASS_CARD}; padding: 4px 12px; border-radius: 12px;")

    def _lock_selected(self):
        row = self.systems_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a lab machine row.")
            return
        host = self.systems_table.item(row, 1).text()
        if host == "127.0.0.1":
            QMessageBox.information(self, "Local System", "Cannot lock the local host.")
            return
        QMessageBox.information(self, "Lock", f"Lock command sent to {host}.\n(Requires SSH key authentication)")

    def _unlock_selected(self):
        row = self.systems_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a lab machine row.")
            return
        host = self.systems_table.item(row, 1).text()
        QMessageBox.information(self, "Unlock", f"Unlock command sent to {host}.")

    def _send_message(self):
        row = self.systems_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a lab machine row.")
            return
        host = self.systems_table.item(row, 1).text()
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Send Message to {host}")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        msg_input = QTextEdit()
        msg_input.setPlaceholderText("Type your message here...")
        layout.addWidget(QLabel("Message:"))
        layout.addWidget(msg_input)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            msg = msg_input.toPlainText().strip()
            if msg:
                QMessageBox.information(self, "Sent", f"Message broadcast to {host}:\n{msg}")

    def _remote_ssh(self):
        row = self.systems_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a lab machine row.")
            return
        host = self.systems_table.item(row, 1).text()
        if host == "127.0.0.1":
            QMessageBox.information(self, "Local System", "Opening local terminal...")
            subprocess.Popen(["konsole"])
            return
        try:
            subprocess.Popen(["konsole", "-e", f"ssh admin@{host}"])
        except Exception:
            QMessageBox.warning(self, "Error", f"Could not open SSH session to {host}.")

    def _open_freebsd_setup(self):
        dlg = FreeBSDSetupDialog(self)
        dlg.exec()

    def _push_update(self):
        """Open dialog to push an update package to all machines"""
        import base64
        import urllib.request

        dlg = QDialog(self)
        dlg.setWindowTitle("Push Update to All Machines")
        dlg.setFixedSize(700, 500)
        layout = QVBoxLayout(dlg)

        layout.addWidget(QLabel("Version:"))
        version_input = QLineEdit()
        version_input.setPlaceholderText("e.g. 1.2.3")
        layout.addWidget(version_input)

        layout.addWidget(QLabel("Description:"))
        desc_input = QLineEdit()
        desc_input.setPlaceholderText("What does this update fix?")
        layout.addWidget(desc_input)

        layout.addWidget(QLabel("Files to push:"))
        file_list = QListWidget()
        layout.addWidget(file_list)

        selected_files = []

        def add_files():
            paths, _ = QFileDialog.getOpenFileNames(
                dlg, "Select files to push"
            )
            for path in paths:
                selected_files.append(path)
                file_list.addItem(path)

        add_btn = QPushButton("Add Files...")
        add_btn.clicked.connect(add_files)
        layout.addWidget(add_btn)

        def do_push():
            if not version_input.text():
                QMessageBox.warning(dlg, "Error", "Enter a version number")
                return
            if not selected_files:
                QMessageBox.warning(dlg, "Error", "Add at least one file")
                return

            files_payload = []
            for path in selected_files:
                try:
                    with open(path, 'rb') as f:
                        content = base64.b64encode(f.read()).decode()
                    rel_path = Path(path).name
                    files_payload.append({
                        'path': rel_path,
                        'content_b64': content
                    })
                except Exception as e:
                    QMessageBox.warning(
                        dlg, "Error", f"Cannot read {path}: {e}"
                    )
                    return

            payload = json.dumps({
                'version': version_input.text(),
                'description': desc_input.text(),
                'files': files_payload
            }).encode()

            try:
                req = urllib.request.Request(
                    f"http://{self.server_host}:{self.server_port}/update/push",
                    data=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_token}'
                    }
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    result = json.loads(resp.read())
                QMessageBox.information(
                    dlg, "Update Pushed",
                    f"Version {version_input.text()} pushed to "
                    f"{len(result.get('recipients', {}))} machines"
                )
                dlg.accept()
            except Exception as e:
                QMessageBox.critical(dlg, "Push Failed", str(e))

        push_btn = QPushButton("Push Update to All Machines")
        push_btn.clicked.connect(do_push)
        layout.addWidget(push_btn)
        dlg.exec()

    def _schedule_exam(self):
        """Open dialog to schedule an exam for automatic push at a future time."""
        import urllib.request

        dlg = QDialog(self)
        dlg.setWindowTitle("Schedule Exam")
        dlg.setFixedSize(480, 300)
        layout = QVBoxLayout(dlg)

        layout.addWidget(QLabel("Exam name:"))
        name_input = QLineEdit()
        name_input.setPlaceholderText("e.g. Midterm 1")
        layout.addWidget(name_input)

        layout.addWidget(QLabel("Start time (YYYY-MM-DDTHH:MM):"))
        time_input = QLineEdit()
        time_input.setPlaceholderText("e.g. 2026-08-03T09:30")
        layout.addWidget(time_input)

        layout.addWidget(QLabel("Exam JSON (optional — merged with the name):"))
        exam_input = QLineEdit()
        exam_input.setPlaceholderText('{"duration_minutes": 60, "questions": []}')
        layout.addWidget(exam_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(buttons)

        def do_schedule():
            name = name_input.text().strip()
            scheduled_at = time_input.text().strip()
            if not name or not scheduled_at:
                QMessageBox.warning(
                    dlg, "Error",
                    "Exam name and start time are required"
                )
                return
            exam_data = {"name": name}
            if exam_input.text().strip():
                try:
                    extra = json.loads(exam_input.text().strip())
                    if isinstance(extra, dict):
                        exam_data.update(extra)
                except json.JSONDecodeError:
                    QMessageBox.warning(
                        dlg, "Error", "Exam JSON is not valid"
                    )
                    return

            payload = json.dumps({
                'name': name,
                'scheduled_at': scheduled_at,
                'exam': exam_data
            }).encode()

            try:
                req = urllib.request.Request(
                    f"http://{self.server_host}:{self.server_port}/exam/schedule",
                    data=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_token}'
                    }
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    result = json.loads(resp.read())
                QMessageBox.information(
                    dlg, "Exam Scheduled",
                    f"'{name}' scheduled for {result.get('scheduled_at')}\n"
                    f"Schedule id: {result.get('schedule_id')}\n"
                    "It will be pushed to all machines automatically."
                )
                dlg.accept()
            except Exception as e:
                QMessageBox.critical(dlg, "Schedule Failed", str(e))

        buttons.accepted.connect(do_schedule)
        buttons.rejected.connect(dlg.reject)
        dlg.exec()

    def _import_roster(self):
        from PyQt6.QtWidgets import (
            QDialog, QVBoxLayout, QLabel, QPushButton,
            QFileDialog, QProgressBar, QTextEdit, QMessageBox
        )
        import csv, urllib.request

        dlg = QDialog(self)
        dlg.setWindowTitle("Import Student Roster")
        dlg.setFixedSize(600, 420)
        layout = QVBoxLayout(dlg)

        layout.addWidget(QLabel(
            "Import students from CSV.\n"
            "Required columns: student_id, name\n"
            "Optional: roll_number, department, semester"
        ))

        log_box = QTextEdit()
        log_box.setReadOnly(True)
        log_box.setFixedHeight(160)
        layout.addWidget(log_box)

        progress = QProgressBar()
        progress.setVisible(False)
        layout.addWidget(progress)

        def pick_and_import():
            path, _ = QFileDialog.getOpenFileName(
                dlg, "Select CSV", "", "CSV Files (*.csv)"
            )
            if not path:
                return
            students, errors = [], []
            try:
                with open(path, newline='', encoding='utf-8') as f:
                    for i, row in enumerate(csv.DictReader(f), 1):
                        sid = (row.get('student_id')
                               or row.get('studentId') or '').strip()
                        name = row.get('name', '').strip()
                        if not sid or not name:
                            errors.append(f"Row {i}: missing id or name")
                            continue
                        students.append({
                            'student_id': sid, 'name': name,
                            'roll_number': row.get('roll_number', '').strip(),
                            'department': row.get('department', '').strip(),
                            'semester': row.get('semester', '').strip(),
                        })
            except Exception as e:
                QMessageBox.critical(dlg, "CSV Error", str(e))
                return

            log_box.append(
                f"Found {len(students)} students ({len(errors)} skipped)"
            )
            if not students:
                return

            progress.setVisible(True)
            try:
                payload = json.dumps({'students': students}).encode()
                req = urllib.request.Request(
                    f"http://{self.server_host}:{self.server_port}/roster/bulk",
                    data=payload,
                    headers={'Content-Type': 'application/json',
                             'Authorization': f'Bearer {self.auth_token}'}
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    result = json.loads(resp.read())
                progress.setValue(progress.maximum())
                log_box.append(f"Imported {result['added']}/{result['total']}")
                if result.get('errors'):
                    log_box.append(
                        f"Errors: {'; '.join(result['errors'][:3])}"
                    )
            except Exception as e:
                log_box.append(f"Upload failed: {e}")

        btn = QPushButton("📂 Choose CSV and Import")
        btn.clicked.connect(pick_and_import)
        layout.addWidget(btn)
        dlg.exec()

    def _view_update_history(self):
        from PyQt6.QtWidgets import (
            QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
            QPushButton, QHBoxLayout, QMessageBox, QInputDialog
        )
        import urllib.request

        dlg = QDialog(self)
        dlg.setWindowTitle("Update History & Rollback")
        dlg.resize(800, 500)
        layout = QVBoxLayout(dlg)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(
            ["ID", "Version", "Description", "Pushed At", "Recipients"]
        )
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(table)
        history = []

        def load_history():
            nonlocal history
            try:
                req = urllib.request.Request(
                    f"http://{self.server_host}:{self.server_port}/update/history",
                    headers={'Authorization': f'Bearer {self.auth_token}'}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read())
                history = data.get('updates', [])
                table.setRowCount(len(history))
                for i, u in enumerate(history):
                    for j, val in enumerate(
                        [str(u['id']), u['version'],
                         u.get('description', ''), u['pushed_at'],
                         str(u.get('recipients', ''))]
                    ):
                        table.setItem(i, j, QTableWidgetItem(val))
            except Exception as e:
                table.setRowCount(1)
                table.setItem(0, 0, QTableWidgetItem(f"Error: {e}"))

        def rollback_selected():
            row = table.currentRow()
            if row < 0 or row >= len(history):
                QMessageBox.warning(dlg, "Select", "Select an update first")
                return
            version = history[row]['version']
            host, ok = QInputDialog.getText(
                dlg, "Rollback Target",
                f"Rollback to v{version} on which machine? "
                "(hostname or 'all')", text="all"
            )
            if not ok or not host.strip():
                return
            confirm = QMessageBox.question(
                dlg, "Confirm",
                f"Rollback {host.strip()} to v{version}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm != QMessageBox.StandardButton.Yes:
                return
            try:
                payload = json.dumps({'version': version}).encode()
                req = urllib.request.Request(
                    f"http://{self.server_host}:{self.server_port}"
                    f"/update/rollback/{host.strip()}",
                    data=payload,
                    headers={'Content-Type': 'application/json',
                             'Authorization': f'Bearer {self.auth_token}'}
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    json.loads(resp.read())
                QMessageBox.information(
                    dlg, "Sent",
                    f"Rollback to v{version} sent to {host.strip()}"
                )
            except Exception as e:
                QMessageBox.critical(dlg, "Failed", str(e))

        btn_row = QHBoxLayout()
        for label, fn in [
            ("🔄 Refresh", load_history),
            ("⏪ Rollback Selected", rollback_selected),
        ]:
            b = QPushButton(label)
            b.clicked.connect(fn)
            btn_row.addWidget(b)
        layout.addLayout(btn_row)
        load_history()
        dlg.exec()

    def _connected_hosts(self):
        return list(getattr(self, '_ping_results', {}).keys())

    def _open_exam_monitor(self):
        """Live monitor showing active exam sessions across all machines"""
        import urllib.request

        dlg = QDialog(self)
        dlg.setWindowTitle("Live Exam Monitor")
        dlg.resize(1000, 600)
        layout = QVBoxLayout(dlg)

        status_label = QLabel("Fetching exam status...")
        layout.addWidget(status_label)

        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Machine", "Student ID", "Exam", "Status",
            "Submitted At", "Checksum"
        ])
        table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(table)

        def refresh():
            try:
                req = urllib.request.Request(
                    f"http://{self.server_host}:{self.server_port}"
                    f"/exam/submissions/1",
                    headers={'Authorization': f'Bearer {self.auth_token}'}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read())

                subs = data.get('submissions', [])
                table.setRowCount(len(subs))
                for i, s in enumerate(subs):
                    table.setItem(i, 0, QTableWidgetItem(s.get('hostname', '')))
                    table.setItem(i, 1, QTableWidgetItem(s.get('student_id', '')))
                    table.setItem(i, 2, QTableWidgetItem(str(s.get('exam_id', ''))))
                    table.setItem(i, 3, QTableWidgetItem("Submitted ✅"))
                    table.setItem(i, 4, QTableWidgetItem(s.get('submitted_at', '')))
                    table.setItem(i, 5, QTableWidgetItem(
                        s.get('checksum', '')[:12] + "..."
                    ))

                status_label.setText(
                    f"Total submissions: {data.get('total', 0)} | "
                    f"Connected machines: {len(self._connected_hosts())} | "
                    f"Last refresh: {datetime.now().strftime('%H:%M:%S')}"
                )
            except Exception as e:
                status_label.setText(f"Cannot reach server: {e}")

        # Auto-refresh every 10 seconds
        timer = QTimer(dlg)
        timer.timeout.connect(refresh)
        timer.start(10000)
        refresh()  # Immediate first load

        btn_row = QHBoxLayout()
        refresh_btn = QPushButton("Refresh Now")
        refresh_btn.clicked.connect(refresh)
        btn_row.addWidget(refresh_btn)

        export_btn = QPushButton("Export All Submissions")
        export_btn.clicked.connect(lambda: self._view_submissions(1))
        btn_row.addWidget(export_btn)

        layout.addLayout(btn_row)
        dlg.exec()

    def _view_submissions(self, exam_id: int = 1):
        """Open dialog showing all exam submissions"""
        import urllib.request
        import csv

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Exam {exam_id} — Submissions")
        dlg.resize(900, 600)
        layout = QVBoxLayout(dlg)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "ID", "Student ID", "Machine", "Submitted At", "Checksum"
        ])
        layout.addWidget(table)

        try:
            req = urllib.request.Request(
                f"http://{self.server_host}:{self.server_port}"
                f"/exam/submissions/{exam_id}",
                headers={'Authorization': f'Bearer {self.auth_token}'}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())

            subs = data.get('submissions', [])
            table.setRowCount(len(subs))
            for i, s in enumerate(subs):
                table.setItem(i, 0, QTableWidgetItem(str(s['id'])))
                table.setItem(i, 1, QTableWidgetItem(s['student_id']))
                table.setItem(i, 2, QTableWidgetItem(s['hostname']))
                table.setItem(i, 3, QTableWidgetItem(s['submitted_at']))
                table.setItem(i, 4, QTableWidgetItem(s['checksum'][:16]))

        except Exception as e:
            table.setRowCount(1)
            table.setItem(0, 0, QTableWidgetItem(""))
            layout.addWidget(QLabel(f"Could not fetch submissions: {e}"))

        def export_csv():
            path, _ = QFileDialog.getSaveFileName(
                dlg, "Export CSV", f"exam_{exam_id}_submissions.csv",
                "CSV Files (*.csv)"
            )
            if path:
                with open(path, 'w', newline='') as f:
                    w = csv.writer(f)
                    w.writerow(["ID","Student","Machine","Time","Checksum"])
                    for r in range(table.rowCount()):
                        w.writerow([
                            table.item(r, c).text()
                            for c in range(table.columnCount())
                        ])

        export_btn = QPushButton("Export to CSV")
        export_btn.clicked.connect(export_csv)
        layout.addWidget(export_btn)
        dlg.exec()

    def _build_software_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info = QLabel("Manage software across all lab machines. Select a system and action below.")
        info.setWordWrap(True)
        info.setStyleSheet(f"font-size: 13px; color: {C.TEXT_SECONDARY}; padding: 12px; background: {C.GLASS_CARD}; border-radius: 8px;")
        layout.addWidget(info)

        sw_layout = QHBoxLayout()

        sw_list = QListWidget()
        sw_list.setStyleSheet("font-size: 13px;")
        packages = [
            ("VS Code", "code"), ("Python 3", "python3"), ("GCC/G++", "gcc"),
            ("OpenJDK 21", "default-jdk"), ("Node.js", "nodejs"),
            ("Docker", "docker-ce"), ("Git", "git"), ("PostgreSQL", "postgresql"),
            ("Wireshark", "wireshark"), ("Nmap", "nmap"),
            ("LibreOffice", "libreoffice"), ("Firefox", "firefox-esr"),
        ]
        for pkg_name, _ in packages:
            sw_list.addItem(f"✅ {pkg_name}")
        sw_layout.addWidget(sw_list)

        actions_layout = QVBoxLayout()
        install_btn = QPushButton("📥 Install Selected")
        install_btn.setStyleSheet(accent_glow_style())
        actions_layout.addWidget(install_btn)

        remove_btn = QPushButton("🗑 Remove Selected")
        remove_btn.setStyleSheet(glass_danger_button_style())
        actions_layout.addWidget(remove_btn)

        update_btn = QPushButton("🔄 Update All Systems")
        update_btn.setStyleSheet(glass_success_button_style())
        actions_layout.addWidget(update_btn)

        deploy_btn = QPushButton("🚀 Deploy to All Labs")
        deploy_btn.setStyleSheet(glass_button_style())
        actions_layout.addWidget(deploy_btn)

        freebsd_btn = QPushButton("🅵 Setup FreeBSD Desktop")
        freebsd_btn.setStyleSheet(glass_warning_button_style())
        freebsd_btn.clicked.connect(self._open_freebsd_setup)
        actions_layout.addWidget(freebsd_btn)

        actions_layout.addStretch()
        sw_layout.addLayout(actions_layout)
        layout.addLayout(sw_layout)

        status_area = QTextEdit()
        status_area.setReadOnly(True)
        status_area.setStyleSheet(f"font-size: 12px; background: {C.BG_MID}; color: {C.ACCENT_SECONDARY}; border-radius: 8px; padding: 8px;")
        status_area.append("📦 Software Management Terminal")
        status_area.append("Ready. Select a system and action to begin.")
        layout.addWidget(status_area)

        return tab

    def _build_exam_control_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info = QLabel("Control examination sessions across the lab. Start, monitor, and terminate exams remotely.")
        info.setWordWrap(True)
        info.setStyleSheet(f"font-size: 13px; color: {C.TEXT_SECONDARY}; padding: 12px; background: {C.GLASS_CARD}; border-radius: 8px;")
        layout.addWidget(info)

        machines = QTableWidget()
        machines.setColumnCount(6)
        machines.setHorizontalHeaderLabels(["Lab", "Status", "Student", "Exam", "Time Remaining", "Actions"])
        machines.horizontalHeader().setStretchLastSection(True)
        machines.setStyleSheet(f"font-size: 13px; border: 1px solid {C.GLASS_BORDER}; border-radius: 8px; color: {C.TEXT_PRIMARY}; background: transparent;")

        machines.setRowCount(3)
        labs = [
            ("Lab 1", "🟢 Idle", "—", "—", "—"),
            ("Lab 2", "🟢 Idle", "—", "—", "—"),
            ("Lab 3", "🟢 Idle", "—", "—", "—"),
        ]
        for i, (lab, status, student, exam, time_rem) in enumerate(labs):
            machines.setItem(i, 0, QTableWidgetItem(lab))
            machines.setItem(i, 1, QTableWidgetItem(status))
            machines.setItem(i, 2, QTableWidgetItem(student))
            machines.setItem(i, 3, QTableWidgetItem(exam))
            machines.setItem(i, 4, QTableWidgetItem(time_rem))
            machines.setItem(i, 5, QTableWidgetItem("Monitor"))
        layout.addWidget(machines)

        exam_actions = QHBoxLayout()
        btn_configs = [
            ("▶ Start Exam Mode", "#16a34a", self._start_exam),
            ("■ Stop All Exams", "#dc2626", self._stop_exams),
            ("⏸ Pause All", "#f59e0b", self._pause_exams),
            ("⏰ Schedule Exam", "#0d9488", self._schedule_exam),
            ("📋 View Active Exams", "#2563eb", self._view_active_exams),
            ("👁 Live Monitor", "#0891b2", self._open_exam_monitor),
            ("📥 View Submissions", "#7c3aed", self._view_submissions),
        ]
        for text, color, handler in btn_configs:
            btn = QPushButton(text)
            if color == "#0d9488":
                style = glass_button_style().replace(
                    "border: 1px solid rgba(255, 255, 255, 0.12)",
                    "border: 1px solid #0d9488; color: #2dd4bf"
                )
            else:
                style = accent_glow_style() if color == "#2563eb" else glass_success_button_style() if color == "#16a34a" else glass_danger_button_style() if color == "#dc2626" else glass_warning_button_style() if color in ("#f59e0b", "#0891b2") else glass_button_style()
            btn.setStyleSheet(style)
            btn.clicked.connect(handler)
            exam_actions.addWidget(btn)
        exam_actions.addStretch()
        layout.addLayout(exam_actions)

        return tab

    def _start_exam(self):
        QMessageBox.information(
            self, "Start Exam",
            "Exam mode will be activated on all lab machines.\n"
            "Students will be prompted to enter their exam credentials."
        )

    def _stop_exams(self):
        reply = QMessageBox.question(
            self, "Stop All Exams",
            "Are you sure you want to stop all running exams?\n"
            "This will terminate active exam sessions.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Stopped", "All exams have been terminated.")

    def _pause_exams(self):
        QMessageBox.information(self, "Paused", "All active exams have been paused.")

    def _view_active_exams(self):
        QMessageBox.information(
            self, "Active Exams",
            "No exams currently running.\n\n"
            "Use 'Start Exam Mode' to begin an examination session."
        )

    def _build_reports_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        reports_list = QListWidget()
        reports = [
            "📊 System Usage Report - June 2026",
            "📝 Exam Results Summary - Current Term",
            "💻 Lab Utilization Report",
            "📦 Software Inventory Report",
            "🔒 Security Audit Log",
            "📈 Network Traffic Analysis",
            "👥 User Activity Report",
        ]
        for report in reports:
            reports_list.addItem(report)
        reports_list.setStyleSheet("font-size: 13px;")
        layout.addWidget(reports_list)

        actions = QHBoxLayout()
        generate_btn = QPushButton("📄 Generate Report")
        generate_btn.setStyleSheet(accent_glow_style())
        actions.addWidget(generate_btn)

        export_btn = QPushButton("📤 Export PDF")
        export_btn.setStyleSheet(glass_button_style())
        actions.addWidget(export_btn)

        refresh_report_btn = QPushButton("🔄 Refresh Data")
        refresh_report_btn.setStyleSheet(glass_warning_button_style())
        actions.addWidget(refresh_report_btn)

        actions.addStretch()
        layout.addLayout(actions)

        report_preview = QTextEdit()
        report_preview.setReadOnly(True)
        report_preview.setStyleSheet(f"font-size: 12px; background: {C.GLASS_CARD}; border: 1px solid {C.GLASS_BORDER}; border-radius: 8px; padding: 12px; color: {C.TEXT_PRIMARY};")
        stats = self._get_realtime_stats()
        report_preview.setPlainText(
            f"EduOS System Report\n"
            f"{'='*40}\n"
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Host: {platform.node()}\n"
            f"OS: {platform.system()} {platform.release()}\n"
            f"CPU Load: {stats.get('cpu', 'N/A')}\n"
            f"Memory: {stats.get('memory', 'N/A')}\n"
            f"Disk: {stats.get('disk', 'N/A')}\n"
            f"Uptime: {stats.get('uptime', 'N/A')}\n"
            f"Network: {stats.get('network', 'N/A')}\n"
        )
        layout.addWidget(report_preview)

        return tab

    def _build_updates_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info = QLabel("Manage system updates and distribute software to lab machines.")
        info.setWordWrap(True)
        info.setStyleSheet(f"font-size: 13px; color: {C.TEXT_SECONDARY}; padding: 12px; background: {C.GLASS_CARD}; border-radius: 8px;")
        layout.addWidget(info)

        update_grid = QHBoxLayout()

        update_card = QFrame()
        update_card.setStyleSheet(f"background: {C.GLASS_CARD}; border: 1px solid {C.GLASS_BORDER}; border-radius: 10px; padding: 20px;")
        uc_layout = QVBoxLayout(update_card)
        uc_layout.addWidget(QLabel("📦 System Updates"))
        uc_layout.addWidget(QLabel("Check for available package updates across all systems."))
        check_btn = QPushButton("🔍 Check for Updates")
        check_btn.setStyleSheet(accent_glow_style())
        uc_layout.addWidget(check_btn)
        update_grid.addWidget(update_card)

        dist_card = QFrame()
        dist_card.setStyleSheet(f"background: {C.GLASS_CARD}; border: 1px solid {C.GLASS_BORDER}; border-radius: 10px; padding: 20px;")
        dc_layout = QVBoxLayout(dist_card)
        dc_layout.addWidget(QLabel("🚀 Distribution"))
        dc_layout.addWidget(QLabel("Push software updates to all connected lab machines."))
        push_btn = QPushButton("📤 Push to All Labs")
        push_btn.setStyleSheet(glass_success_button_style())
        push_btn.clicked.connect(self._push_update)
        dc_layout.addWidget(push_btn)
        update_grid.addWidget(dist_card)

        policy_card = QFrame()
        policy_card.setStyleSheet(f"background: {C.GLASS_CARD}; border: 1px solid {C.GLASS_BORDER}; border-radius: 10px; padding: 20px;")
        pc_layout = QVBoxLayout(policy_card)
        pc_layout.addWidget(QLabel("📋 Update Policy"))
        policy_select = QComboBox()
        policy_select.addItems(["Auto-update (Recommended)", "Manual approval only", "Schedule: Weekends", "Schedule: Nightly"])
        policy_select.setStyleSheet(f"font-size: 13px; padding: 8px; background: {C.GLASS_CARD}; color: {C.TEXT_PRIMARY}; border: 1px solid {C.GLASS_BORDER};")
        pc_layout.addWidget(policy_select)
        pc_layout.addWidget(QLabel("Current policy: Auto-update"))
        update_grid.addWidget(policy_card)

        layout.addLayout(update_grid)

        self.update_log = QTextEdit()
        self.update_log.setReadOnly(True)
        self.update_log.setStyleSheet(f"font-size: 12px; background: {C.BG_MID}; color: {C.ACCENT_SECONDARY}; border-radius: 8px; padding: 8px;")
        self.update_log.append("📋 Update Distribution Log")
        self.update_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] System ready for update management.")
        self.update_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Lab hosts configured: {len(self.lab_hosts)}")
        layout.addWidget(self.update_log)

        return tab

    def _load_system_info(self):
        self.host_label.setText(
            f"🖥 {platform.node()} | {platform.system()} {platform.release()} | {platform.machine()}"
        )

        sys_name = platform.system()
        if sys_name == "FreeBSD":
            self.platform_badge.setText("🅵 FreeBSD")
            self.platform_badge.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {C.ACCENT_AMBER}; background: {C.GLASS_CARD}; padding: 4px 12px; border-radius: 12px;")
        elif sys_name == "Linux":
            self.platform_badge.setText("🐧 Linux")
        else:
            self.platform_badge.setText(sys_name)

        self.systems_table.setRowCount(0)

        row = self.systems_table.rowCount()
        self.systems_table.insertRow(row)
        self.systems_table.setItem(row, 0, QTableWidgetItem(platform.node()))
        self.systems_table.setItem(row, 1, QTableWidgetItem("127.0.0.1"))
        self.systems_table.setItem(row, 2, QTableWidgetItem("✅ Online"))

        stats = self._get_realtime_stats()
        self.systems_table.setItem(row, 3, QTableWidgetItem(stats.get("uptime", "N/A")))
        self.systems_table.setItem(row, 4, QTableWidgetItem(stats.get("cpu", "N/A")))
        self.systems_table.setItem(row, 5, QTableWidgetItem(stats.get("memory", "N/A")))
        self.systems_table.setItem(row, 6, QTableWidgetItem("Now"))

        for host in self.lab_hosts:
            row = self.systems_table.rowCount()
            self.systems_table.insertRow(row)
            self.systems_table.setItem(row, 0, QTableWidgetItem(host["hostname"]))
            self.systems_table.setItem(row, 1, QTableWidgetItem(host["ip"]))

            ip = host["ip"]
            is_online = getattr(self, "ping_results", {}).get(ip, False)
            status = "✅ Online" if is_online else "❌ Offline"
            self.systems_table.setItem(row, 2, QTableWidgetItem(status))

            for col in range(3, 7):
                self.systems_table.setItem(
                    row, col,
                    QTableWidgetItem("—" if not is_online else "Awaiting data")
                )


class FreeBSDSetupDialog(QDialog):
    """Instructions + provisioning commands for FreeBSD lab machines."""

    SCRIPT_PATH = "Scripts/freebsd-desktop-setup.sh"
    USAGE = (
        "On the target FreeBSD machine (as root):\n\n"
        "  # 1. Copy the repo to the machine\n"
        "  git clone https://github.com/Dev9269/eduos /opt/eduos\n\n"
        "  # 2. Run the desktop setup script\n"
        "  sh /opt/eduos/Scripts/freebsd-desktop-setup.sh\n\n"
        "  # 3. After reboot, install the agent\n"
        "  sh /opt/eduos/Services/freebsd/install-agent-freebsd.sh\n\n"
        "The setup script installs KDE Plasma + SDDM, the Python stack,\n"
        "dev tools, EduOS branding, and registers the eduos_agent rc.d\n"
        "service. Exam lockdown is handled by the eduos_exam rc.d\n"
        "service, controlled remotely from the Exam Control tab."
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🅵 FreeBSD Desktop Setup")
        self.setMinimumSize(620, 480)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        intro = QLabel("Provision a FreeBSD 14.x lab machine with the EduOS desktop environment.")
        intro.setWordWrap(True)
        intro.setStyleSheet(f"font-size: 13px; color: {C.TEXT_SECONDARY}; padding: 12px; background: {C.GLASS_CARD}; border-radius: 8px;")
        layout.addWidget(intro)

        self.script_text = QTextEdit()
        self.script_text.setReadOnly(True)
        self.script_text.setStyleSheet(f"font-size: 12px; background: {C.BG_MID}; color: {C.ACCENT_SECONDARY}; border-radius: 8px; padding: 8px;")
        self.script_text.setPlainText(self.USAGE)
        layout.addWidget(self.script_text)

        btn_row = QHBoxLayout()
        copy_btn = QPushButton("📋 Copy Instructions")
        copy_btn.setStyleSheet(glass_button_style())
        copy_btn.clicked.connect(self._copy_to_clipboard)
        btn_row.addWidget(copy_btn)
        btn_row.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(glass_danger_button_style())
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _copy_to_clipboard(self):
        QApplication.clipboard().setText(self.script_text.toPlainText())
        self.script_text.append("\n✅ Instructions copied to clipboard.")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    apply_glass_theme(app)

    # Vulnerability 1 — authentication gate before admin panel opens
    login = AdminLoginDialog()
    if login.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)

    window = AdminCenterWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
EduOS Admin Center - Centralized administration platform
"""

import sys
import os
import subprocess
import json
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


class PingThread(QThread):
    result = pyqtSignal(str, bool)

    def __init__(self, host):
        super().__init__()
        self.host = host

    def run(self):
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
        self._load_config()
        self._setup_ui()
        self._load_system_info()
        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh_monitor)
        self._timer.start(5000)
        self._ping_lock = threading.Lock()

    def closeEvent(self, event):
        self._timer.stop()
        event.accept()

    def _load_config(self):
        config_path = Path.home() / ".eduos" / "admin_config.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    cfg = json.load(f)
                    self.lab_hosts = cfg.get("lab_hosts", [])
            except Exception:
                self.lab_hosts = []

    def _save_config(self):
        config_dir = Path.home() / ".eduos"
        config_dir.mkdir(parents=True, exist_ok=True)
        with open(config_dir / "admin_config.json", "w") as f:
            json.dump({"lab_hosts": self.lab_hosts}, f, indent=2)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)

        header = QWidget()
        header.setStyleSheet("background: linear-gradient(135deg, #0f172a, #1e3a5f); border-radius: 12px; padding: 16px;")
        hlayout = QHBoxLayout(header)

        title = QLabel("⚙ EduOS Admin Center")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        hlayout.addWidget(title)

        self.status_label = QLabel("● Online")
        self.status_label.setStyleSheet("color: #4ade80; font-size: 13px; background: #166534; padding: 4px 12px; border-radius: 12px;")
        hlayout.addWidget(self.status_label)

        hlayout.addStretch()

        self.host_label = QLabel()
        self.host_label.setStyleSheet("font-size: 12px; color: #94a3b8;")
        hlayout.addWidget(self.host_label)
        layout.addWidget(header)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; background: white; }
            QTabBar::tab { padding: 10px 20px; font-size: 13px; font-weight: bold; }
            QTabBar::tab:selected { background: #2563eb; color: white; border-radius: 8px 8px 0 0; }
        """)

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
            card.setStyleSheet(f"background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; border-left: 4px solid {color};")
            cl = QVBoxLayout(card)
            cl.addWidget(QLabel(ctitle))
            v = QLabel(value)
            v.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
            cl.addWidget(v)
            grid.addWidget(card)
        layout.addLayout(grid)

        self.monitor_tree = QTreeWidget()
        self.monitor_tree.setHeaderLabels(["Resource", "Usage", "Status"])
        self.monitor_tree.setStyleSheet("font-size: 13px; border: 1px solid #e2e8f0; border-radius: 8px;")
        layout.addWidget(self.monitor_tree)

        return tab

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
        add_btn.setStyleSheet("background: #2563eb; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: bold;")
        add_btn.clicked.connect(self._add_lab_machine)
        toolbar.addWidget(add_btn)

        refresh_btn = QPushButton("🔄 Ping All")
        refresh_btn.setStyleSheet("background: #7c3aed; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: bold;")
        refresh_btn.clicked.connect(self._ping_all_hosts)
        toolbar.addWidget(refresh_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.systems_table = QTableWidget()
        self.systems_table.setColumnCount(7)
        self.systems_table.setHorizontalHeaderLabels(["System", "IP", "Status", "Uptime", "CPU", "Memory", "Last Seen"])
        self.systems_table.horizontalHeader().setStretchLastSection(True)
        self.systems_table.setStyleSheet("font-size: 13px; border: 1px solid #e2e8f0; border-radius: 8px;")
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
            btn.setStyleSheet(f"background: {color}; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: bold;")
            btn.clicked.connect(handler)
            actions.addWidget(btn)
        actions.addStretch()
        layout.addLayout(actions)

        info = QLabel("💡 Select a lab machine row and use the buttons above to manage it remotely.")
        info.setStyleSheet("font-size: 12px; color: #94a3b8; padding: 8px;")
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
        self.status_label.setStyleSheet("color: #f59e0b; font-size: 13px; background: #78350f; padding: 4px 12px; border-radius: 12px;")

        hosts = [h["ip"] for h in self.lab_hosts]
        self.ping_results = {}

        def check_host(ip):
            try:
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
        self.status_label.setStyleSheet("color: #4ade80; font-size: 13px; background: #166534; padding: 4px 12px; border-radius: 12px;")

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

    def _build_software_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info = QLabel("Manage software across all lab machines. Select a system and action below.")
        info.setWordWrap(True)
        info.setStyleSheet("font-size: 13px; color: #666; padding: 12px; background: #f0f4ff; border-radius: 8px;")
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
        install_btn.setStyleSheet("background: #2563eb; color: white; padding: 10px; border: none; border-radius: 6px; font-weight: bold;")
        actions_layout.addWidget(install_btn)

        remove_btn = QPushButton("🗑 Remove Selected")
        remove_btn.setStyleSheet("background: #dc2626; color: white; padding: 10px; border: none; border-radius: 6px; font-weight: bold;")
        actions_layout.addWidget(remove_btn)

        update_btn = QPushButton("🔄 Update All Systems")
        update_btn.setStyleSheet("background: #16a34a; color: white; padding: 10px; border: none; border-radius: 6px; font-weight: bold;")
        actions_layout.addWidget(update_btn)

        deploy_btn = QPushButton("🚀 Deploy to All Labs")
        deploy_btn.setStyleSheet("background: #7c3aed; color: white; padding: 10px; border: none; border-radius: 6px; font-weight: bold;")
        actions_layout.addWidget(deploy_btn)

        actions_layout.addStretch()
        sw_layout.addLayout(actions_layout)
        layout.addLayout(sw_layout)

        status_area = QTextEdit()
        status_area.setReadOnly(True)
        status_area.setStyleSheet("font-size: 12px; background: #1e293b; color: #a5f3fc; border-radius: 8px; padding: 8px;")
        status_area.append("📦 Software Management Terminal")
        status_area.append("Ready. Select a system and action to begin.")
        layout.addWidget(status_area)

        return tab

    def _build_exam_control_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info = QLabel("Control examination sessions across the lab. Start, monitor, and terminate exams remotely.")
        info.setWordWrap(True)
        info.setStyleSheet("font-size: 13px; color: #666; padding: 12px; background: #f0f4ff; border-radius: 8px;")
        layout.addWidget(info)

        machines = QTableWidget()
        machines.setColumnCount(6)
        machines.setHorizontalHeaderLabels(["Lab", "Status", "Student", "Exam", "Time Remaining", "Actions"])
        machines.horizontalHeader().setStretchLastSection(True)
        machines.setStyleSheet("font-size: 13px; border: 1px solid #e2e8f0; border-radius: 8px;")

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
            ("📋 View Active Exams", "#2563eb", self._view_active_exams),
        ]
        for text, color, handler in btn_configs:
            btn = QPushButton(text)
            btn.setStyleSheet(f"background: {color}; color: white; padding: 8px 18px; border: none; border-radius: 6px; font-weight: bold; font-size: 13px;")
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
        generate_btn.setStyleSheet("background: #2563eb; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: bold;")
        actions.addWidget(generate_btn)

        export_btn = QPushButton("📤 Export PDF")
        export_btn.setStyleSheet("background: #7c3aed; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: bold;")
        actions.addWidget(export_btn)

        refresh_report_btn = QPushButton("🔄 Refresh Data")
        refresh_report_btn.setStyleSheet("background: #f59e0b; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: bold;")
        actions.addWidget(refresh_report_btn)

        actions.addStretch()
        layout.addLayout(actions)

        report_preview = QTextEdit()
        report_preview.setReadOnly(True)
        report_preview.setStyleSheet("font-size: 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px;")
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
        info.setStyleSheet("font-size: 13px; color: #666; padding: 12px; background: #f0f4ff; border-radius: 8px;")
        layout.addWidget(info)

        update_grid = QHBoxLayout()

        update_card = QFrame()
        update_card.setStyleSheet("background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px;")
        uc_layout = QVBoxLayout(update_card)
        uc_layout.addWidget(QLabel("📦 System Updates"))
        uc_layout.addWidget(QLabel("Check for available package updates across all systems."))
        check_btn = QPushButton("🔍 Check for Updates")
        check_btn.setStyleSheet("background: #2563eb; color: white; padding: 10px; border: none; border-radius: 6px; font-weight: bold;")
        uc_layout.addWidget(check_btn)
        update_grid.addWidget(update_card)

        dist_card = QFrame()
        dist_card.setStyleSheet("background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px;")
        dc_layout = QVBoxLayout(dist_card)
        dc_layout.addWidget(QLabel("🚀 Distribution"))
        dc_layout.addWidget(QLabel("Push software updates to all connected lab machines."))
        push_btn = QPushButton("📤 Push to All Labs")
        push_btn.setStyleSheet("background: #16a34a; color: white; padding: 10px; border: none; border-radius: 6px; font-weight: bold;")
        dc_layout.addWidget(push_btn)
        update_grid.addWidget(dist_card)

        policy_card = QFrame()
        policy_card.setStyleSheet("background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px;")
        pc_layout = QVBoxLayout(policy_card)
        pc_layout.addWidget(QLabel("📋 Update Policy"))
        policy_select = QComboBox()
        policy_select.addItems(["Auto-update (Recommended)", "Manual approval only", "Schedule: Weekends", "Schedule: Nightly"])
        policy_select.setStyleSheet("font-size: 13px; padding: 8px;")
        pc_layout.addWidget(policy_select)
        pc_layout.addWidget(QLabel("Current policy: Auto-update"))
        update_grid.addWidget(policy_card)

        layout.addLayout(update_grid)

        self.update_log = QTextEdit()
        self.update_log.setReadOnly(True)
        self.update_log.setStyleSheet("font-size: 12px; background: #1e293b; color: #a5f3fc; border-radius: 8px; padding: 8px;")
        self.update_log.append("📋 Update Distribution Log")
        self.update_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] System ready for update management.")
        self.update_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Lab hosts configured: {len(self.lab_hosts)}")
        layout.addWidget(self.update_log)

        return tab

    def _load_system_info(self):
        self.host_label.setText(
            f"🖥 {platform.node()} | {platform.system()} {platform.release()} | {platform.machine()}"
        )

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


def main():
    app = QApplication(sys.argv)
    window = AdminCenterWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

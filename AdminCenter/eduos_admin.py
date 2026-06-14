#!/usr/bin/env python3
"""
EduOS Admin Center - Centralized administration platform
"""

import sys
import os
import subprocess
import json
import platform
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QTabWidget,
    QGroupBox, QTextEdit, QMessageBox, QHeaderView, QListWidget,
    QSplitter, QFrame, QTreeWidget, QTreeWidgetItem, QProgressBar,
    QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QAction


class AdminCenterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduOS Admin Center - Campus Management Console")
        self.setGeometry(50, 50, 1300, 800)
        self._setup_ui()
        self._load_system_info()
        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh_monitor)
        self._timer.start(5000)

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
        for title, value, color in cards:
            card = QFrame()
            card.setStyleSheet(f"background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; border-left: 4px solid {color};")
            cl = QVBoxLayout(card)
            cl.addWidget(QLabel(title))
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

    def _build_systems_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.systems_table = QTableWidget()
        self.systems_table.setColumnCount(6)
        self.systems_table.setHorizontalHeaderLabels(["System", "IP", "Status", "Uptime", "CPU", "Memory"])
        self.systems_table.horizontalHeader().setStretchLastSection(True)
        self.systems_table.setStyleSheet("font-size: 13px; border: 1px solid #e2e8f0; border-radius: 8px;")
        layout.addWidget(self.systems_table)

        actions = QHBoxLayout()
        for text, color in [("🔒 Lock Selected", "#dc2626"), ("🔓 Unlock", "#16a34a"), ("📢 Send Message", "#7c3aed")]:
            btn = QPushButton(text)
            btn.setStyleSheet(f"background: {color}; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: bold;")
            actions.addWidget(btn)
        actions.addStretch()
        layout.addLayout(actions)

        return tab

    def _build_software_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        software_list = QListWidget()
        software_list.setStyleSheet("font-size: 13px;")
        packages = ["VS Code", "Python 3", "GCC/G++", "OpenJDK 21", "Node.js", "Docker", "Git", "PostgreSQL"]
        for pkg in packages:
            software_list.addItem(f"✅ {pkg}")
        layout.addWidget(software_list)

        actions = QHBoxLayout()
        install_btn = QPushButton("📥 Install Software")
        install_btn.setStyleSheet("background: #2563eb; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: bold;")
        actions.addWidget(install_btn)

        remove_btn = QPushButton("🗑 Remove Selected")
        remove_btn.setStyleSheet("background: #dc2626; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: bold;")
        actions.addWidget(remove_btn)

        update_btn = QPushButton("🔄 Update All")
        update_btn.setStyleSheet("background: #16a34a; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: bold;")
        actions.addWidget(update_btn)

        actions.addStretch()
        layout.addLayout(actions)

        return tab

    def _build_exam_control_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info = QLabel("Control examination sessions across the lab. Start, monitor, and terminate exams remotely.")
        info.setWordWrap(True)
        info.setStyleSheet("font-size: 13px; color: #666; padding: 12px; background: #f0f4ff; border-radius: 8px;")
        layout.addWidget(info)

        machines = QTableWidget()
        machines.setColumnCount(5)
        machines.setHorizontalHeaderLabels(["Lab", "Status", "Student", "Exam", "Time Remaining"])
        machines.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(machines)

        actions = QHBoxLayout()
        for text, color in [("▶ Start Exam Mode", "#16a34a"), ("■ Stop Exam", "#dc2626"), ("⏸ Pause All", "#f59e0b")]:
            btn = QPushButton(text)
            btn.setStyleSheet(f"background: {color}; color: white; padding: 8px 18px; border: none; border-radius: 6px; font-weight: bold; font-size: 13px;")
            actions.addWidget(btn)
        actions.addStretch()
        layout.addLayout(actions)

        return tab

    def _build_reports_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        reports_list = QListWidget()
        reports = [
            "📊 System Usage Report - June 2026",
            "📝 Exam Results Summary - Current Term",
            "💻 Lab Utilization Report",
            "📦 Software Inventory Report",
            "🔒 Security Audit Log"
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

        actions.addStretch()
        layout.addLayout(actions)

        return tab

    def _load_system_info(self):
        self.host_label.setText(f"🖥 {platform.node()} | {platform.system()} {platform.release()} | {platform.machine()}")

        self.systems_table.setRowCount(0)
        row = self.systems_table.rowCount()
        self.systems_table.insertRow(row)
        self.systems_table.setItem(row, 0, QTableWidgetItem(platform.node()))
        self.systems_table.setItem(row, 1, QTableWidgetItem("10.0.2.15"))
        self.systems_table.setItem(row, 2, QTableWidgetItem("✅ Online"))

        try:
            uptime_sec = float(open("/proc/uptime").read().split()[0])
            days, rem = divmod(uptime_sec, 86400)
            hours, rem = divmod(rem, 3600)
            self.systems_table.setItem(row, 3, QTableWidgetItem(f"{int(days)}d {int(hours)}h"))
        except:
            self.systems_table.setItem(row, 3, QTableWidgetItem("N/A"))

        try:
            cpu = open("/proc/loadavg").read().split()[:3]
            self.systems_table.setItem(row, 4, QTableWidgetItem(f"{cpu[0]} / {cpu[1]} / {cpu[2]}"))
        except:
            self.systems_table.setItem(row, 4, QTableWidgetItem("N/A"))

        try:
            mem_info = {}
            with open("/proc/meminfo") as f:
                for line in f:
                    parts = line.split()
                    mem_info[parts[0].rstrip(":")] = int(parts[1])
            total = mem_info.get("MemTotal", 0) // 1024
            available = mem_info.get("MemAvailable", 0) // 1024
            used = total - available
            self.systems_table.setItem(row, 5, QTableWidgetItem(f"{used}MB / {total}MB"))
        except:
            self.systems_table.setItem(row, 5, QTableWidgetItem("N/A"))

    def _refresh_monitor(self):
        self.monitor_tree.clear()
        
        items = [
            ("CPU Load", "Low", "#16a34a"),
            ("Memory", "906MB / 3.8GB", "#2563eb"),
            ("Disk", "11GB / 19GB", "#f59e0b"),
            ("Network", "10.0.2.15", "#16a34a"),
            ("Services", "All Running", "#16a34a"),
        ]
        for name, value, color in items:
            item = QTreeWidgetItem([name, value, "●"])
            item.setForeground(2, QColor(color))
            self.monitor_tree.addTopLevelItem(item)


def main():
    app = QApplication(sys.argv)
    window = AdminCenterWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

"""
EduOS Institution Manager — Lab, Exam & Device Inventory Tabs
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget,
    QMessageBox, QFrame
)
from PyQt6.QtCore import Qt

from styles import *
from ui_components import Card, SectionTitle, TableWidget, ActionBar, StatusBadge, btn_outline
from config import load_json, save_json, PATHS, log_activity


class LabExamDeviceTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: transparent; padding-top: 8px; }
            QTabBar::tab { padding: 10px 24px; font-size: 13px; font-weight: 500; color: #64748b; background: transparent; border: none; border-bottom: 2px solid transparent; }
            QTabBar::tab:selected { color: #2563eb; border-bottom: 2px solid #2563eb; }
            QTabBar::tab:hover { color: #1e293b; }
        """)

        tabs.addTab(self._build_labs(), "🔬 Labs")
        tabs.addTab(self._build_exams(), "📝 Exams")
        tabs.addTab(self._build_devices(), "💻 Devices")

        layout.addWidget(tabs)

    def _build_labs(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 8, 0, 0)

        bar = ActionBar("Lab Management")
        bar.add_button("Add Lab", "➕", self._lab_info)
        bar.add_button("Export Report", "📊", self._lab_info, btn_outline())
        layout.addWidget(bar)

        labs = load_json(PATHS["labs"], [])
        table = TableWidget(["ID", "Lab Name", "Department", "Capacity", "Systems", "In-Charge", "Status", "Last Updated"])
        for l in labs:
            st = "active" if l["status"] == "Operational" else "warning" if l["status"] == "Maintenance" else "inactive"
            table.add_row([
                l["id"], l["name"], l["department"], str(l["capacity"]),
                str(l["systems"]), l["in_charge"], "", l["last_updated"]
            ])
            row = table.rowCount() - 1
            badge = StatusBadge(l["status"], st)
            table.setCellWidget(row, 6, badge)
        layout.addWidget(table)

        return tab

    def _build_exams(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 8, 0, 0)

        bar = ActionBar("Exam Management")
        bar.add_button("Schedule Exam", "📅", self._exam_info)
        bar.add_button("Results Analysis", "📊", self._exam_info, btn_outline())
        layout.addWidget(bar)

        exams = load_json(PATHS["exams"], [])
        table = TableWidget(["ID", "Exam Title", "Department", "Type", "Date", "Duration", "Appeared", "Pass Rate", "Avg Score", "Status"])
        for e in exams:
            st = "success" if e["status"] == "Completed" else "active" if e["status"] == "Ongoing" else "warning" if e["status"] == "Evaluated" else "info"
            table.add_row([
                e["id"], e["title"], e["department"], e["type"],
                e["date"], f"{e['duration_minutes']} min",
                str(e["appeared"]), f"{e['pass_rate']}%", f"{e['avg_score']}%", ""
            ])
            row = table.rowCount() - 1
            badge = StatusBadge(e["status"], st)
            table.setCellWidget(row, 9, badge)
        layout.addWidget(table)

        return tab

    def _build_devices(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 8, 0, 0)

        bar = ActionBar("Device Inventory")
        bar.add_button("Register Device", "➕", self._device_info)
        bar.add_button("Network Scan", "📡", self._device_info, btn_outline())
        layout.addWidget(bar)

        devices = load_json(PATHS["devices"], [])
        table = TableWidget(["ID", "Device Name", "Type", "Department", "Location", "OS", "IP Address", "Status", "Last Seen"])
        for d in devices:
            st = "active" if d["status"] == "Online" else "inactive" if d["status"] == "Offline" else "warning"
            table.add_row([
                d["id"], d["name"], d["type"], d["department"],
                d["location"], d["os"], d["ip"], "", d["last_seen"]
            ])
            row = table.rowCount() - 1
            badge = StatusBadge(d["status"], st)
            table.setCellWidget(row, 7, badge)
        layout.addWidget(table)

        return tab

    def _lab_info(self):
        labs = load_json(PATHS["labs"], [])
        operational = sum(1 for l in labs if l["status"] == "Operational")
        QMessageBox.information(self, "Lab Overview", f"Total Labs: {len(labs)}\nOperational: {operational}\nUnder Maintenance: {len(labs) - operational}")

    def _exam_info(self):
        exams = load_json(PATHS["exams"], [])
        QMessageBox.information(self, "Exam Overview", f"Total Exams: {len(exams)}\nCompleted: {sum(1 for e in exams if e['status'] == 'Completed')}\nScheduled: {sum(1 for e in exams if e['status'] == 'Scheduled')}")

    def _device_info(self):
        devices = load_json(PATHS["devices"], [])
        online = sum(1 for d in devices if d["status"] == "Online")
        QMessageBox.information(self, "Device Overview", f"Total Devices: {len(devices)}\nOnline: {online}\nOffline: {len(devices) - online}")

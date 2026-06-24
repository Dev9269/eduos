#!/usr/bin/env python3
"""
EduOS Institution Manager — Main Entry Point
Flagship application for managing educational institution deployments.
"""

import sys
import os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QMessageBox, QFrame, QStatusBar,
    QSplashScreen
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPalette, QColor

from styles import *
from config import institution_config, get_analytics, log_activity, BASE_DIR

# Import all tabs
from dashboard import DashboardTab
from institution_profile import InstitutionProfileTab
from department_course import DepartmentCourseTab
from people_management import PeopleManagementTab
from lab_exam_inventory import LabExamDeviceTab
from module_management import ModuleManagementTab
from update_management import UpdateManagementTab
from centralized_management import CentralizedManagementTab
from ai_assistant import AIAssistantTab
from demo_mode import DemoModeTab


class InstitutionManagerWindow(QMainWindow):
    def __init__(self, demo_mode=False):
        super().__init__()
        self.demo_mode = demo_mode
        self.setWindowTitle("EduOS Institution Manager")
        self.setGeometry(100, 50, 1400, 900)
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(APP_STYLESHEET)

        self._setup_ui()
        self._show_startup_info()

    def _setup_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top navigation bar
        nav = QFrame()
        nav.setStyleSheet(f"background: {SECONDARY}; padding: 0;")
        nav.setFixedHeight(52)
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("🏫 EduOS Institution Manager")
        logo.setStyleSheet("font-size: 16px; font-weight: 700; color: white;")
        nav_layout.addWidget(logo)

        nav_layout.addStretch()

        # Institution name from config
        cfg = institution_config()
        inst_name = QLabel(f"{cfg['name']}  |  v{cfg['version']}")
        inst_name.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.6);")
        nav_layout.addWidget(inst_name)

        if self.demo_mode:
            demo_badge = QLabel("🎬 DEMO MODE")
            demo_badge.setStyleSheet("background: #f59e0b; color: white; padding: 4px 12px; border-radius: 10px; font-size: 11px; font-weight: 700; margin-left: 8px;")
            nav_layout.addWidget(demo_badge)

        layout.addWidget(nav)

        # Main content: Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: transparent; }
            QTabBar::tab { padding: 12px 20px; font-size: 13px; font-weight: 500; color: #64748b;
                         background: transparent; border: none; border-bottom: 2px solid transparent; }
            QTabBar::tab:selected { color: #2563eb; border-bottom: 2px solid #2563eb; background: #f8fafc; }
            QTabBar::tab:hover { color: #1e293b; background: #f1f5f9; }
        """)

        self.tabs.addTab(DashboardTab(self), "📊 Dashboard")
        self.tabs.addTab(InstitutionProfileTab(self), "🏛 Institution")

        # Combined tabs
        self.tabs.addTab(DepartmentCourseTab(self), "📚 Departments & Courses")
        self.tabs.addTab(PeopleManagementTab(self), "👥 People")
        self.tabs.addTab(LabExamDeviceTab(self), "🔬 Labs, Exams & Devices")
        self.tabs.addTab(ModuleManagementTab(self), "🧩 Modules")
        self.tabs.addTab(UpdateManagementTab(self), "🔄 Updates")
        self.tabs.addTab(CentralizedManagementTab(self), "☁️ Central Mgmt")
        self.tabs.addTab(AIAssistantTab(self), "🤖 AI Assistant")
        self.tabs.addTab(DemoModeTab(self), "🎬 Demo")

        layout.addWidget(self.tabs, 1)

        # Status bar
        analytics = get_analytics()
        self.statusBar().showMessage(
            f"🏫 {cfg['name']}  |  "
            f"👨‍🎓 {analytics['total_students']} Students  |  "
            f"👨‍🏫 {analytics['total_faculty']} Faculty  |  "
            f"📚 {analytics['active_courses']} Courses  |  "
            f"💻 {analytics['device_count']} Devices  |  "
            f"📊 {analytics['avg_score']}% Avg Score  |  "
            f"EduOS Platform v{cfg['version']}"
        )
        self.statusBar().setStyleSheet(f"background: {SECONDARY}; color: rgba(255,255,255,0.7); font-size: 12px; padding: 4px;")

    def _show_startup_info(self):
        log_activity("Application Started", "EduOS Institution Manager launched")
        if self.demo_mode:
            QMessageBox.information(self, "🎬 Demo Mode Active",
                "EduOS Institution Manager is running in DEMO MODE.\n\n"
                "This mode showcases the complete platform capabilities:\n"
                "• Modular Architecture with Module Registry\n"
                "• Institution Management Dashboard\n"
                "• Centralized Management Platform\n"
                "• AI Education Assistant\n"
                "• Institutional Branding System\n\n"
                "Use the Demo tab for a guided tour."
            )


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set application-wide font
    font = QFont("Inter", 10)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)

    # Check for demo mode flag
    demo_mode = "--demo" in sys.argv or "-d" in sys.argv

    window = InstitutionManagerWindow(demo_mode)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

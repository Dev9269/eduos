"""
EduOS Institution Manager — Dashboard Tab
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from styles import *
from ui_components import StatCard, SectionTitle, Card, MiniChart, ActionBar, StatusBadge
from config import get_analytics, get_activity_log


class DashboardTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_widget = QWidget()
        scroll.setWidget(scroll_widget)
        content = QVBoxLayout(scroll_widget)
        content.setSpacing(16)

        # Welcome header
        welcome = QWidget()
        welcome.setStyleSheet(f"background: linear-gradient(135deg, {PRIMARY}, {PRIMARY_DARK}); border-radius: 16px; padding: 24px;")
        wl = QHBoxLayout(welcome)
        wl.setContentsMargins(24, 20, 24, 20)
        wt = QVBoxLayout()
        ti = QLabel("Welcome to EduOS Institution Manager")
        ti.setStyleSheet("font-size: 24px; font-weight: 700; color: white;")
        wt.addWidget(ti)
        su = QLabel("Manage your entire educational institution from one platform. Monitor, control, and analyze everything.")
        su.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.8);")
        su.setWordWrap(True)
        wt.addWidget(su)
        wl.addLayout(wt, 1)
        wl.addWidget(QLabel("🏫"), alignment=Qt.AlignmentFlag.AlignRight)
        wl.itemAt(1).widget().setStyleSheet("font-size: 48px;")
        content.addWidget(welcome)

        # KPI Row
        analytics = get_analytics()
        kpis = [
            (analytics["total_students"], "Total Students", "🎓", "↑ 12% vs last semester", True, PRIMARY),
            (analytics["total_faculty"], "Faculty Members", "👨‍🏫", "↑ 3 new this month", True, SUCCESS),
            (analytics["active_courses"], "Active Courses", "📚", "↑ 8 new this year", True, ACCENT),
            (analytics["total_exams"], "Exams Conducted", "📝", f"{analytics['pass_rate']}% pass rate", True, INFO),
        ]
        kpi_grid = QHBoxLayout()
        kpi_grid.setSpacing(12)
        for val, label, icon, trend, up, color in kpis:
            card = StatCard(val, label, icon, trend, up, color)
            kpi_grid.addWidget(card)
        content.addLayout(kpi_grid)

        # Second KPI row
        kpis2 = [
            (analytics["device_count"], "Registered Devices", "💻", f"{analytics['online_devices']} online", True, PRIMARY),
            (analytics["active_labs"], "Active Labs", "🔬", "All operational", True, SUCCESS),
            (f"{analytics['avg_score']}%", "Average Score", "📊", "↑ 2.3% improvement", True, ACCENT),
            (f"{analytics['storage_used_gb']} GB", "Storage Used", "💾", "85% of capacity", False, WARNING),
        ]
        kpi_grid2 = QHBoxLayout()
        kpi_grid2.setSpacing(12)
        for val, label, icon, trend, up, color in kpis2:
            card = StatCard(val, label, icon, trend, up, color)
            kpi_grid2.addWidget(card)
        content.addLayout(kpi_grid2)

        # Middle section: charts + activity
        mid = QHBoxLayout()
        mid.setSpacing(16)

        # Chart card
        chart_card = QFrame()
        chart_card.setStyleSheet(card_style())
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(16, 16, 16, 16)
        chart_title = QLabel("📈 Exam Performance Trend")
        chart_title.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {TEXT_PRIMARY};")
        chart_layout.addWidget(chart_title)

        chart_sub = QLabel("Average scores across last 12 examinations")
        chart_sub.setStyleSheet(f"font-size: 11px; color: {TEXT_SECONDARY}; padding-bottom: 8px;")
        chart_layout.addWidget(chart_sub)

        chart = MiniChart([55, 58, 52, 60, 62, 58, 65, 68, 72, 70, 75, 78], PRIMARY)
        chart_layout.addWidget(chart)

        chart_labels = QHBoxLayout()
        for label in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
            l = QLabel(label)
            l.setStyleSheet(f"font-size: 9px; color: {TEXT_MUTED};")
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chart_labels.addWidget(l)
        chart_layout.addLayout(chart_labels)

        # Security chart
        sec_chart = MiniChart([90, 85, 88, 92, 95, 91, 93, 96, 98, 97, 99, 100], SUCCESS)
        chart_layout.addWidget(sec_chart)
        sec_label = QLabel("Security Compliance (%)")
        sec_label.setStyleSheet(f"font-size: 11px; color: {TEXT_SECONDARY}; padding-top: 4px;")
        chart_layout.addWidget(sec_label)

        mid.addWidget(chart_card, 3)

        # Activity feed
        activity_card = QFrame()
        activity_card.setStyleSheet(card_style())
        act_layout = QVBoxLayout(activity_card)
        act_layout.setContentsMargins(16, 16, 16, 16)
        act_title = QLabel("⏱ Recent Activity")
        act_title.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {TEXT_PRIMARY};")
        act_layout.addWidget(act_title)

        activity_data = get_activity_log(8)
        for entry in activity_data:
            item = QWidget()
            item.setStyleSheet("border-bottom: 1px solid #f1f5f9; padding: 4px 0;")
            il = QHBoxLayout(item)
            il.setContentsMargins(0, 4, 0, 4)
            dot = QLabel("●")
            dot.setStyleSheet(f"font-size: 8px; color: {PRIMARY};")
            il.addWidget(dot)
            text = QLabel(entry["action"])
            text.setStyleSheet(f"font-size: 12px; color: {TEXT_PRIMARY}; font-weight: 500;")
            il.addWidget(text, 1)
            time = QLabel(entry["timestamp"][11:16] if "T" in entry["timestamp"] else "")
            time.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED};")
            il.addWidget(time)
            act_layout.addWidget(item)

        mid.addWidget(activity_card, 2)
        content.addLayout(mid)

        # Quick Actions
        actions_title = SectionTitle("⚡ Quick Actions")
        content.addWidget(actions_title)

        actions = QHBoxLayout()
        actions.setSpacing(12)
        quick_items = [
            ("Create New Course", "📖", "Add a new course to the curriculum", PRIMARY),
            ("Schedule Exam", "📝", "Set up a new examination", SUCCESS),
            ("Add Student", "👨‍🎓", "Enroll a new student", ACCENT),
            ("Generate Report", "📊", "Export institutional analytics", INFO),
            ("Run Update", "🔄", "Check for system updates", DANGER),
        ]
        for title, icon, desc, color in quick_items:
            card = QFrame()
            card.setStyleSheet(f"background: white; border: 1px solid {BORDER}; border-radius: 12px; padding: 16px;")
            card.setFixedWidth(180)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(12, 12, 12, 12)
            ic = QLabel(icon)
            ic.setStyleSheet("font-size: 28px;")
            cl.addWidget(ic)
            t = QLabel(title)
            t.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {TEXT_PRIMARY};")
            cl.addWidget(t)
            d = QLabel(desc)
            d.setStyleSheet(f"font-size: 11px; color: {TEXT_SECONDARY};")
            d.setWordWrap(True)
            cl.addWidget(d)
            actions.addWidget(card)

        actions.addStretch()
        content.addLayout(actions)

        layout.addWidget(scroll)
